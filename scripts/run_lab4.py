"""Run Postman and Swagger UI tests against disposable PostgreSQL/Redis and Uvicorn."""
import argparse
import asyncio
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import asyncpg
import httpx
from alembic import command
from alembic.config import Config
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from tests.integration.conftest import _apply_env

OUT=ROOT/'docs/lab4/evidence'
OUT.mkdir(parents=True,exist_ok=True)


def run_command(args, log, env=None):
    started=time.monotonic()
    with (OUT/log).open('w') as output:
        result=subprocess.run(args,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=240)
    print(f'{log}: exit={result.returncode}, {time.monotonic()-started:.1f}s',flush=True)
    return result.returncode


async def elevate(user):
    connection=await asyncpg.connect(host=os.environ['POSTGRES_HOST'],port=int(os.environ['POSTGRES_PORT']),
      user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],database=os.environ['POSTGRES_DB'])
    try:
        await connection.execute("UPDATE users SET role='SUPERADMIN' WHERE id=$1",UUID(user))
    finally: await connection.close()


def redact(value):
    if isinstance(value,list): return [redact(item) for item in value]
    if not isinstance(value,dict): return value
    key=str(value.get('key','')).lower()
    if key in ['cookie','set-cookie','authorization','password','admin_password'] or key.startswith('token_'):
        return {**value,'value':'<redacted>'}
    output={}
    for k,v in value.items():
        if k in ['password','admin_password'] or k.startswith('token_'): output[k]='<redacted>'
        elif k=='raw' and isinstance(v,str):
            try: output[k]=json.dumps(redact(json.loads(v)),ensure_ascii=False)
            except (ValueError,TypeError): output[k]=v
        else: output[k]=redact(v)
    return output


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--only',choices=['all','api','ui'],default='all')
    args=parser.parse_args()
    node=os.environ.get('NODE_BINARY') or shutil.which('node') or '/usr/lib/chatgpt/resources/cua_node/bin/node'
    started=datetime.now(ZoneInfo('Europe/Minsk')).isoformat()
    results={'started':started,'frontend':'API only; layout/mobile/cross-browser checks not applicable','runner':'Newman + Playwright Chromium', 'commands':{}}
    postgres=PostgresContainer('postgres:16-alpine',username='postgres',password='postgres',dbname='trafficmaster')
    redis=RedisContainer('redis:7-alpine',password='secret')
    with postgres,redis:
        _apply_env(postgres,redis)
        cfg=Config(str(ROOT/'alembic.ini')); command.upgrade(cfg,'head'); command.check(cfg)
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0)); port=listener.getsockname()[1]
        url=f'http://127.0.0.1:{port}'
        env={**os.environ,'LAB4_BASE_URL':url,'LAB4_EVIDENCE_DIR':str(OUT/'ui')}
        with (OUT/'server.log').open('w') as server_log,subprocess.Popen(
            [sys.executable,'-m','uvicorn','trafficmaster.web:create_fastapi_app','--factory','--host','127.0.0.1','--port',str(port)],
            cwd=ROOT,stdout=server_log,stderr=subprocess.STDOUT,env=env) as server:
            try:
                with httpx.Client(base_url=url,trust_env=False,timeout=10) as api:
                    deadline=time.monotonic()+30
                    while True:
                        assert server.poll() is None,'Server startup failed'
                        try:
                            if api.get('/healthcheck/ready').status_code==200: break
                        except httpx.TransportError: pass
                        assert time.monotonic()<deadline,'Readiness timeout'
                        time.sleep(0.1)
                    spec=api.get('/openapi.json'); spec.raise_for_status()
                    (ROOT/'postman/openapi.json').write_text(json.dumps(spec.json(),ensure_ascii=False,indent=2)+'\n')
                    subprocess.run([sys.executable,'scripts/build_postman_collection.py'],cwd=ROOT,check=True)
                    if args.only in ['all','api']:
                        email=f'lab4_admin_{uuid4().hex[:8]}@example.com'; password='LabAdminSecure456'
                        signup=api.post('/v1/auth/signup',json={'email':email,'name':'Lab-Superadmin','password':password})
                        assert signup.status_code==201,signup.text
                        asyncio.run(elevate(signup.json()['id']))
                        arguments=[node,str(ROOT/'postman/node_modules/newman/bin/newman.js'),'run',
                          'postman/TrafficMaster.postman_collection.json','-e','postman/local.postman_environment.json',
                          '--env-var','base_url='+url,'--env-var','admin_email='+email,'--env-var','admin_password='+password,
                          '-r','cli,json,junit','--reporter-json-export',str(OUT/'newman.json'),
                          '--reporter-junit-export',str(OUT/'newman.xml')]
                        results['commands']['newman']=run_command(arguments,'newman.log',env)
                        raw=json.loads((OUT/'newman.json').read_text())
                        (OUT/'newman.json').write_text(json.dumps(redact(raw),ensure_ascii=False,indent=2)+'\n')
                        results['api_stats']=raw['run']['stats']
                        results['api_failures']=[{'name':x.get('source',{}).get('name'),'error':x['error'].get('message')} for x in raw['run']['failures']]
                    if args.only in ['all','ui']:
                        results['commands']['playwright']=run_command([sys.executable,'-m','pytest','tests/e2e','-q','--no-cov',
                          '--browser','chromium','-k','not failure_screenshot_probe','--tb=short',
                          '--junitxml='+str(OUT/'ui.xml')],'playwright.log',env)
                        probe_env={**env,'LAB4_SCREENSHOT_PROBE':'1','LAB4_EVIDENCE_DIR':str(OUT/'screenshot-probe')}
                        results['commands']['screenshot_probe']=run_command([sys.executable,'-m','pytest','tests/e2e','-q','--no-cov',
                          '--browser','chromium','-k','failure_screenshot_probe','--tb=short'],'screenshot-probe.log',probe_env)
                        results['failure_capture_verified']=results['commands']['screenshot_probe']==1 and bool(list((OUT/'screenshot-probe').glob('*.png')))
                    results['commands']['error_security_unit']=run_command([sys.executable,'-m','pytest',
                      'tests/unit/presentation/http/v1/common/test_exception_handler.py','-q','--no-cov','--tb=short'], 'error-security.log',env)
            finally:
                server.terminate()
                try: server.wait(timeout=10)
                except subprocess.TimeoutExpired: server.kill(); server.wait(timeout=5)
    results['finished']=datetime.now(ZoneInfo('Europe/Minsk')).isoformat()
    results['versions']={'python':sys.version,'node':subprocess.check_output([node,'--version'],text=True).strip()}
    (OUT/'run.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False,indent=2),flush=True)
    return int(any(results['commands'].get(key,0) != 0 for key in ['newman','playwright','error_security_unit'])
               or ('failure_capture_verified' in results and not results['failure_capture_verified']))


if __name__=='__main__': sys.exit(main())
