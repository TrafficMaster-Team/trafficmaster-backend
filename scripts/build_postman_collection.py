"""Build a portable Postman v2.1 collection from the current OpenAPI contract."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / 'postman/openapi.json'
spec = json.loads(SPEC_PATH.read_text())
definitions = json.loads(json.dumps(spec['components']['schemas']).replace('#/components/schemas/', '#/definitions/'))
items = []
coverage = []
count = 0


def canonical(path):
    path = path.split('?')[0]
    for kind, names in {'user_id':['user_a','user_b','managed_user'], 'deck_id':['deck_a','deck_b','deck_alt','copy_deck'], 'card_id':['card_a','card_b','copy_card'], 'deck_config_id':['config_a','config_b','config_alt','copy_config']}.items():
        for name in names:
            path=path.replace('{{'+name+'}}','{'+kind+'}')
    if '/tags/' in path: path=path.rsplit('/',1)[0]+'/{tag}'
    return path


def add(folder, title, method, path, code=200, body=None, actor='a', check='', save=None, route=None, pre=''):
    global count
    count+=1
    route=route or canonical(path)
    op=spec['paths'].get(route,{}).get(method.lower(),{})
    response_schema=op.get('responses',{}).get(str(code),{}).get('content',{}).get('application/json',{}).get('schema')
    lines=[f'pm.test("HTTP {code}", () => pm.response.to.have.status({code}));']
    if response_schema:
        root=json.loads(json.dumps(response_schema).replace('#/components/schemas/','#/definitions/'))
        lines+=[f'if (pm.response.code === {code}) '+'pm.test("Response JSON schema", () => { const schema='+json.dumps(root)+'; schema.definitions=JSON.parse(pm.collectionVariables.get("schema_definitions")); pm.response.to.have.jsonSchema(schema); });']
    elif code==204:
        lines+=['pm.test("Empty 204 body", () => pm.expect(pm.response.text()).to.eql(""));']
    if code>=400:
        lines+=['pm.test("No stack, paths or SQL in client error", () => pm.expect(pm.response.text()).not.to.match(/Traceback|File \\"|\\/home\\/|\\/app\\/|sqlalchemy|asyncpg|SELECT\\s+.+FROM|INSERT\\s+INTO/i));']
    if code<300 and code!=204:
        lines+=['const j=pm.response.json();']
    if save:
        for key,expression in save.items(): lines.append(f'if (pm.response.code === {code}) pm.collectionVariables.set({json.dumps(key)}, {expression});')
    if check: lines.append(f'if (pm.response.code === {code}) '+'pm.test("Field values and scenario invariants", () => { '+check+' });')
    token='""' if actor=='guest' else f'pm.collectionVariables.get("token_{actor}") || ""'
    prerequest=pre+'\npm.request.headers.upsert({key:"Cookie",value:"access_token="+('+token+')});'
    request={'method':method,'header':[{'key':'Content-Type','value':'application/json'}], 'url':'{{base_url}}'+path,
             'description':f'Canonical operation: {method} {route}. Actor: {actor}. Expected HTTP {code}.'}
    if body is not None: request['body']={'mode':'raw','raw':json.dumps(body,ensure_ascii=False),'options':{'raw':{'language':'json'}}}
    item={'name':f'R{count:03} | {title}', 'request':request,
          'protocolProfileBehavior':{'disableCookies':True},
          'event':[{'listen':'prerequest','script':{'type':'text/javascript','exec':prerequest.splitlines()}},
                   {'listen':'test','script':{'type':'text/javascript','exec':lines}}]}
    target=items[-1] if items and items[-1]['name']==folder else None
    if target is None: target={'name':folder,'item':[]}; items.append(target)
    target['item'].append(item)
    coverage.append({'name':item['name'],'method':method,'route':route,'expected':code,'actor':actor,'positive':code<300})
    return item


def config(owner,name='Lab config'):
    return {'owner_id':owner,'name':name,'daily_limits':{'new_cards_per_day':2,'max_reviews_per_day':20},
            'new_cards':{'learning_steps':[1,10],'graduating_interval':1,'easy_interval':4,'new_card_order':'sequential'},
            'lapses':{'relearning_steps':[10],'min_interval':1},
            'advanced':{'max_interval':36500,'ease_factor':2.5,'easy_factor':1.3,'interval_modifier':1.0,'hard_interval':1.2,'new_interval':0.0}}


def card(deck):
    return {'deck_id':deck,'question':'What does red mean?','answerOptions':[{'text':'Stop','isCorrect':True,'rationale':'Red prohibits movement'}],'hint':'Safety','tags':['signals']}


def identity(who):
    add('01 Auth',f'Signup {who}','POST','/v1/auth/signup',201,
        {'email':'{{email_'+who+'}}','name':'Lab4-User'+who.upper(),'password':'{{password}}'},actor='guest',
        check='pm.expect(j.id).to.match(/^[0-9a-f-]{36}$/);',save={'user_'+who:'j.id'})
    login(who)


def login(who, email=None, password='{{password}}'):
    add('01 Auth' if who!='admin' else '07 Administration',f'Login {who}','POST','/v1/auth/login',204,
        {'email':email or '{{email_'+who+'}}','password':password},actor='guest',
        check='const cookie=pm.response.headers.get("Set-Cookie"); pm.expect(cookie).to.match(/access_token=/); pm.expect(cookie).to.match(/HttpOnly/i);',
        save={'token_'+who:'(pm.response.headers.get("Set-Cookie") || "").match(/access_token=([^;]+)/)?.[1] || ""'})


init='''const run=Date.now().toString(36)+pm.variables.replaceIn("{{$guid}}").slice(0,4);
pm.collectionVariables.set("run_id",run);
for (const who of ["a","b"]) { pm.collectionVariables.set("email_"+who,"lab4_"+who+"_"+run+"@example.com"); pm.collectionVariables.set("token_"+who,""); }
pm.collectionVariables.set("token_admin","");'''
add('00 Service','Index','GET','/',check='pm.expect(j).to.be.an("object"); pm.expect(Object.keys(j).length).to.be.greaterThan(0);',actor='guest',pre=init)
add('00 Service','Liveness','GET','/healthcheck/live',check='pm.expect(j.status).to.eql("alive");',actor='guest')
add('00 Service','Readiness','GET','/healthcheck/ready',check='pm.expect(j).to.deep.equal({status:"ready",database:"up",cache:"up"});',actor='guest')
identity('a')
add('01 Auth','Current identity','GET','/v1/auth/me',check='pm.expect(j.id).to.eql(pm.collectionVariables.get("user_a")); pm.expect(j.email).to.eql(pm.collectionVariables.get("email_a"));')
add('01 Auth','Wrong password','POST','/v1/auth/login',401,{'email':'{{email_a}}','password':'WrongSecure123'},actor='guest')
add('01 Auth','Duplicate email','POST','/v1/auth/signup',409,{'email':'{{email_a}}','name':'Lab4-Duplicate','password':'{{password}}'},actor='guest')
add('01 Auth','Invalid identity','POST','/v1/auth/signup',422,{'email':'invalid','name':'x','password':'1'},actor='guest')

for key in ['a','alt']:
    add('02 Configuration',f'Create config {key}','POST','/v1/deck-config/',201,config('{{user_a}}','Config '+key),save={'config_'+key:'j.id'},check='pm.expect(j.id).to.be.a("string");')
add('02 Configuration','Read config','GET','/v1/deck-config/{{config_a}}',check='pm.expect(j.owner_id).to.eql(pm.collectionVariables.get("user_a")); pm.expect(j.daily_limits.new_cards_per_day).to.eql(2); pm.expect(j.new_cards.learning_steps).to.eql([1,10]); pm.expect(j.lapses.relearning_steps).to.eql([10]); pm.expect(j.advanced.ease_factor).to.eql(2.5);')
add('02 Configuration','List own configs','GET','/v1/deck-config/?user_id={{user_a}}',check='pm.expect(j.configs || j.deck_configs).to.be.an("array");')
changes={'name':{'name':'Updated config'},'daily-limits':{'new_cards_per_day':3,'max_reviews_per_day':20},'new-cards':config('')['new_cards'],'advanced':config('')['advanced'],'lapses':config('')['lapses']}
for part,body in changes.items(): add('02 Configuration','Change '+part,'PATCH','/v1/deck-config/{{config_a}}/'+part,204,body)
add('02 Configuration','Verify config changes','GET','/v1/deck-config/{{config_a}}',check='pm.expect(j.name).to.eql("Updated config"); pm.expect(j.daily_limits.new_cards_per_day).to.eql(3); pm.expect(j.new_cards.learning_steps).to.eql([1,10]); pm.expect(j.advanced.max_interval).to.eql(36500); pm.expect(j.lapses.min_interval).to.eql(1);')
add('02 Configuration','Invalid limit','PATCH','/v1/deck-config/{{config_a}}/daily-limits',400,{'new_cards_per_day':0,'max_reviews_per_day':20})
for key in ['a','alt']:
    add('03 Decks',f'Create deck {key}','POST','/v1/deck/',201,{'owner_id':'{{user_a}}','deck_config_id':'{{config_a}}','title':'Traffic '+key,'is_public':False},save={'deck_'+key:'j.id'},check='pm.expect(j.id).to.be.a("string");')
add('03 Decks','Read private deck','GET','/v1/deck/{{deck_a}}',check='pm.expect(j.owner_id).to.eql(pm.collectionVariables.get("user_a")); pm.expect(j.title).to.eql("Traffic a"); pm.expect(j.is_public).to.eql(false);')
add('03 Decks','Own decks','GET','/v1/deck/?user_id={{user_a}}',check='pm.expect(j.decks.map(x=>x.id)).to.include(pm.collectionVariables.get("deck_a"));')
add('03 Decks','Change title','PATCH','/v1/deck/{{deck_a}}/title',204,{'title':'Updated traffic'})
add('03 Decks','Change description','PATCH','/v1/deck/{{deck_a}}/description',204,{'description':'Updated description'})
add('03 Decks','Assign config','PATCH','/v1/deck/{{deck_a}}/config',204,{'deck_config_id':'{{config_alt}}'})
add('03 Decks','Verify changes','GET','/v1/deck/{{deck_a}}',check='pm.expect(j.title).to.eql("Updated traffic"); pm.expect(j.description).to.eql("Updated description"); pm.expect(j.deck_config_id).to.eql(pm.collectionVariables.get("config_alt"));')
add('03 Decks','Invalid UUID','GET','/v1/deck/not-a-uuid',422,route='/v1/deck/{deck_id}')
add('03 Decks','Missing entity','GET','/v1/deck/00000000-0000-0000-0000-000000000000',404,route='/v1/deck/{deck_id}')
add('04 Cards','Create card','POST','/v1/card/',201,card('{{deck_a}}'),save={'card_a':'j.id'},check='pm.expect(j.id).to.be.a("string");')
add('04 Cards','Read card','GET','/v1/card/{{card_a}}',check='pm.expect(j.question).to.eql("What does red mean?"); pm.expect(j.answerOptions[0]).to.include({text:"Stop",isCorrect:true,rationale:"Red prohibits movement"}); pm.expect(j.hint).to.eql("Safety");')
add('04 Cards','List cards','GET','/v1/card/?deck_id={{deck_a}}',check='pm.expect(j.cards.map(x=>x.id)).to.include(pm.collectionVariables.get("card_a"));')
add('04 Cards','Change question','PATCH','/v1/card/{{card_a}}/question',204,{'question':'Updated question'})
add('04 Cards','Change content','PATCH','/v1/card/{{card_a}}/content',204,{'answerOptions':[{'text':'Wait','isCorrect':True,'rationale':'Safety first'}],'hint':'Updated hint'})
add('04 Cards','Set image metadata','PATCH','/v1/card/{{card_a}}/image',204,{'image_path':'images/signal.png'})
add('04 Cards','Add tag','POST','/v1/card/{{card_a}}/tags',204,{'tag':'lab'})
add('04 Cards','Verify card changes','GET','/v1/card/{{card_a}}',check='pm.expect(j.question).to.eql("Updated question"); pm.expect(j.answerOptions[0].text).to.eql("Wait"); pm.expect(j.hint).to.eql("Updated hint"); pm.expect(j.tags).to.include("lab"); pm.expect(j.image_path).to.eql("images/signal.png");')
add('04 Cards','Remove tag','DELETE','/v1/card/{{card_a}}/tags/lab',204)
add('04 Cards','Clear image','PATCH','/v1/card/{{card_a}}/image',204,{'image_path':None})
for dest in ['deck_alt','deck_a']: add('04 Cards','Move card to '+dest,'PATCH','/v1/card/{{card_a}}/deck',204,{'deck_id':'{{'+dest+'}}'})
add('04 Cards','Verify move and clears','GET','/v1/card/{{card_a}}',check='pm.expect(j.deck_id).to.eql(pm.collectionVariables.get("deck_a")); pm.expect(j.image_path).to.eql(null); pm.expect(j.tags).not.to.include("lab");')
add('04 Cards','Empty question','POST','/v1/card/',422,card('{{deck_a}}')|{'question':''})
add('05 Learning','Review queue','GET','/v1/review/queue?deck_id={{deck_a}}&limit=1',check='pm.expect(j.items.length).to.eql(1); pm.expect(j.items[0].card_id).to.eql(pm.collectionVariables.get("card_a"));')
add('05 Learning','Preview','GET','/v1/review/card/{{card_a}}/preview',check='pm.expect(j.items.map(x=>x.rating).sort()).to.eql([1,2,3,4]);')
add('05 Learning','No progress after preview','GET','/v1/review/card/{{card_a}}/progress',404)
for rating,state in [(1,'learning'),(3,'learning'),(3,'review'),(1,'relearning'),(3,'review')]:
    add('05 Learning','Transition '+state,'POST','/v1/review/card/{{card_a}}',200,{'rating':rating},check=f'pm.expect(j.state).to.eql("{state}"); pm.expect(Date.parse(j.next_review_at)).to.be.greaterThan(Date.now());')
add('05 Learning','Read persisted progress','GET','/v1/review/card/{{card_a}}/progress',check='pm.expect(j.state).to.eql("review"); pm.expect(j.card_id).to.eql(pm.collectionVariables.get("card_a"));')
for path in ['/v1/review/card/{{card_a}}/logs','/v1/review/logs?deck_id={{deck_a}}']:
    add('05 Learning','Five history rows','GET',path,check='pm.expect(j.logs.length).to.eql(5); pm.expect(j.logs.every(x=>x.user_id===pm.collectionVariables.get("user_a"))).to.eql(true);')
add('05 Learning','Statistics','GET','/v1/review/deck/{{deck_a}}/stats',check='pm.expect(j.total_cards).to.eql(1); pm.expect(j.review_count).to.eql(1);')
add('05 Learning','Reset progress','POST','/v1/review/card/{{card_a}}/reset',204)
add('05 Learning','Reset removes progress','GET','/v1/review/card/{{card_a}}/progress',404)
add('05 Learning','Reset keeps history','GET','/v1/review/card/{{card_a}}/logs',check='pm.expect(j.logs.length).to.eql(5);')
add('05 Learning','Invalid rating','POST','/v1/review/card/{{card_a}}',422,{'rating':5})
identity('b')
add('06 Security','Other user config','POST','/v1/deck-config/',201,config('{{user_b}}'),actor='b',save={'config_b':'j.id'},check='pm.expect(j.id).to.be.a("string");')
add('06 Security','Other user deck','POST','/v1/deck/',201,{'owner_id':'{{user_b}}','deck_config_id':'{{config_b}}','title':'Private B'},actor='b',save={'deck_b':'j.id'},check='pm.expect(j.id).to.be.a("string");')
add('06 Security','Other user card','POST','/v1/card/',201,card('{{deck_b}}'),actor='b',save={'card_b':'j.id'},check='pm.expect(j.id).to.be.a("string");')
for path in ['/v1/auth/me','/v1/user/{{user_a}}','/v1/deck/{{deck_a}}','/v1/card/{{card_a}}','/v1/deck-config/{{config_a}}','/v1/review/queue?deck_id={{deck_a}}','/v1/review/card/{{card_a}}/progress','/v1/review/card/{{card_a}}/preview','/v1/review/card/{{card_a}}/logs','/v1/review/deck/{{deck_a}}/stats']:
    add('06 Security','Anonymous direct URL','GET',path,401,actor='guest')
for path in ['/v1/user/{{user_a}}','/v1/deck/{{deck_a}}','/v1/card/{{card_a}}','/v1/deck-config/{{config_a}}','/v1/review/queue?deck_id={{deck_a}}','/v1/review/card/{{card_a}}/preview','/v1/review/card/{{card_a}}/logs','/v1/review/deck/{{deck_a}}/stats']:
    add('06 Security','IDOR read denied','GET',path,403,actor='b')
for method,path,body in [('PATCH','/v1/deck/{{deck_a}}/title',{'title':'Stolen'}),('PATCH','/v1/card/{{card_a}}/question',{'question':'Stolen'}),('PATCH','/v1/deck-config/{{config_a}}/name',{'name':'Stolen'}),('PATCH','/v1/user/{{user_a}}/password',{'password':'ChangedSecure456'}),('POST','/v1/review/card/{{card_a}}',{'rating':4}),('POST','/v1/review/card/{{card_a}}/reset',None),('PATCH','/v1/card/{{card_b}}/deck',{'deck_id':'{{deck_a}}'}),('POST','/v1/deck-config/',config('{{user_a}}')),('POST','/v1/card/',card('{{deck_a}}'))]:
    add('06 Security','IDOR mutation denied',method,path,403,body,actor='b')
add('06 Security','Missing route','GET','/v1/route-that-does-not-exist',404,actor='guest')
add('06 Security','Original data unchanged','GET','/v1/card/{{card_a}}',check='pm.expect(j.question).to.eql("Updated question"); pm.expect(j.deck_id).to.eql(pm.collectionVariables.get("deck_a"));')
add('06 Security','Foreign private deck is not polluted','GET','/v1/card/?deck_id={{deck_a}}',check='pm.expect(j.cards.length).to.eql(1);')
add('06 Security','Publish own deck','PATCH','/v1/deck/{{deck_a}}/privacy',204,{'is_public':True})
add('06 Security','Public catalogue','GET','/v1/deck/public?limit=100',actor='guest',check='pm.expect(j.decks.map(x=>x.id)).to.include(pm.collectionVariables.get("deck_a")); pm.expect(j.decks.map(x=>x.id)).not.to.include(pm.collectionVariables.get("deck_b"));')
add('06 Security','Copy public deck','POST','/v1/deck/{{deck_a}}/copy',201,actor='b',save={'copy_deck':'j.deck_id','copy_config':'j.deck_config_id'},check='pm.expect(j.deck_id).not.to.eql(pm.collectionVariables.get("deck_a")); pm.expect(j.deck_config_id).not.to.eql(pm.collectionVariables.get("config_alt"));')
add('06 Security','Read copy','GET','/v1/deck/{{copy_deck}}',actor='b',check='pm.expect(j.owner_id).to.eql(pm.collectionVariables.get("user_b")); pm.expect(j.is_public).to.eql(false);')
login('admin',email='{{admin_email}}',password='{{admin_password}}')
add('07 Administration','Create managed user','POST','/v1/user/',201,{'email':'managed_{{run_id}}@example.com','username':'Managed-User','password':'{{password}}','role':'user'},actor='admin',save={'managed_user':'j.id'},check='pm.expect(j.id).to.be.a("string");')
add('07 Administration','List users','GET','/v1/user/?limit=100',actor='admin',check='pm.expect(j.users.map(x=>x.id)).to.include(pm.collectionVariables.get("managed_user"));')
add('07 Administration','Read managed user','GET','/v1/user/{{managed_user}}',actor='admin',check='pm.expect(j.role).to.eql("user");')
add('07 Administration','Grant admin','PATCH','/v1/user/{{managed_user}}/admin',204,actor='admin')
add('07 Administration','Verify admin','GET','/v1/user/{{managed_user}}',actor='admin',check='pm.expect(j.role).to.eql("admin");')
add('07 Administration','Revoke admin','DELETE','/v1/user/{{managed_user}}/admin',204,actor='admin')
add('07 Administration','Activate user','PATCH','/v1/user/{{managed_user}}/activate',204,actor='admin')
add('07 Administration','Change username','PATCH','/v1/user/{{managed_user}}/username',204,{'username':'Changed-User'},actor='admin')
add('07 Administration','Change email','PATCH','/v1/user/{{managed_user}}/email',204,{'email':'changed_{{run_id}}@example.com'},actor='admin')
add('07 Administration','Verify managed changes','GET','/v1/user/{{managed_user}}',actor='admin',check='pm.expect(j.name).to.eql("Changed-User"); pm.expect(j.email).to.eql("changed_"+pm.collectionVariables.get("run_id")+"@example.com");')
add('07 Administration','Own aggregate stats','GET','/v1/user/stats',check='pm.expect(j).to.be.an("object"); pm.expect(Object.keys(j).length).to.be.greaterThan(0);')
add('07 Administration','Delete managed user','DELETE','/v1/user/{{managed_user}}',204,actor='admin')
add('07 Administration','Verify deletion','GET','/v1/user/{{managed_user}}',404,actor='admin')
add('08 Finalization','Change own password','PATCH','/v1/user/{{user_a}}/password',204,{'password':'ChangedSecure456'})
add('08 Finalization','Old cookie revoked','GET','/v1/auth/me',401)
add('08 Finalization','Old password rejected','POST','/v1/auth/login',401,{'email':'{{email_a}}','password':'{{password}}'},actor='guest')
login('a',password='ChangedSecure456')
add('08 Finalization','Logout','POST','/v1/auth/logout',204)
add('08 Finalization','Logout revokes old cookie','GET','/v1/auth/me',401)
login('a',password='ChangedSecure456')
add('08 Finalization','Delete card','DELETE','/v1/card/{{card_a}}',204)
add('08 Finalization','Deleted card','GET','/v1/card/{{card_a}}',404)
for key in ['a','alt']:
    add('08 Finalization','Delete deck '+key,'DELETE','/v1/deck/{{deck_'+key+'}}',204)
for key in ['a','alt']:
    add('08 Finalization','Delete config '+key,'DELETE','/v1/deck-config/{{config_'+key+'}}',204)
add('09 Security role escalation','User cannot grant own admin role','PATCH','/v1/user/{{user_b}}/admin',403,actor='b')
add('09 Security role escalation','Role must remain user','GET','/v1/auth/me',actor='b',check='pm.expect(j.role).to.eql("user");')
add('09 Security role escalation','Restore disposable user role','DELETE','/v1/user/{{user_b}}/admin',204,actor='admin')

collection={'info':{'name':'TrafficMaster — Lab 4 API and security','schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json','description':'All OpenAPI operations. Cookies from login are chained explicitly. Synthetic fixtures only. Run on a disposable lab environment.'},
            'variable':[{'key':'schema_definitions','value':json.dumps(definitions)},{'key':'password','value':'LearningSecure123'}], 'item':items}
(ROOT/'postman/TrafficMaster.postman_collection.json').write_text(json.dumps(collection,ensure_ascii=False,indent=2)+'\n')
(ROOT/'postman/local.postman_environment.json').write_text(json.dumps({'name':'TrafficMaster local (disposable)','values':[{'key':k,'value':v,'enabled':True} for k,v in {'base_url':'http://127.0.0.1:8080','admin_email':'SET_BY_LAB_RUNNER','admin_password':'SET_BY_LAB_RUNNER'}.items()],'_postman_variable_scope':'environment'},indent=2)+'\n')
(ROOT/'postman/coverage-map.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
covered={(c['method'].lower(),c['route']) for c in coverage if c['positive']}
all_ops={(m,p) for p,ms in spec['paths'].items() for m in ms if m in ['get','post','patch','put','delete']}
print('Requests:',count,'positive operations:',len(covered & all_ops),'/',len(all_ops),'missing:',sorted(all_ops-covered))
assert not all_ops-covered
