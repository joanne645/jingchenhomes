/* 城市生活指南 · 共用脚本（导航高亮、片区展开、地图）
   地图数据在访客浏览器中实时读取：
   - 底图：OpenStreetMap 标准瓦片（© OpenStreetMap contributors）
   - 城市边界、学区范围：U.S. Census Bureau TIGERweb REST 服务（现行图层）
   - 地点定位：U.S. Census Geocoder（按页面中已核实的街道地址）
   任何一项读取失败时，页面保留文字说明与官方地图按钮。 */
(function(){
'use strict';
var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};

/* ---------- 导航 ---------- */
var links=$$('.subnav a');
if(links.length && 'IntersectionObserver' in window){
  var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a});
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){links.forEach(function(a){a.classList.remove('on')});var a=map[e.target.id];if(a){a.classList.add('on');
      var p=a.parentNode;var l=a.offsetLeft-p.clientWidth/2+a.clientWidth/2;if(p.scrollTo)p.scrollTo({left:l,behavior:'smooth'});}}
  })},{rootMargin:'-45% 0px -50% 0px'});
  Object.keys(map).forEach(function(id){var el=document.getElementById(id);if(el)io.observe(el)});
}
function openHash(){var id=decodeURIComponent(location.hash.slice(1));if(!id)return;var el=document.getElementById(id);
  if(el&&el.tagName==='DETAILS'){el.open=true;setTimeout(function(){el.scrollIntoView()},30)}}
window.addEventListener('hashchange',openHash);openHash();

/* ---------- 地图 ---------- */
var G=window.GUIDE, box=$('#citymap');
if(!G||!box)return;
var TIGER='https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/';
var GEOCODER='https://geocoding.geo.census.gov/geocoder/locations/onelineaddress';
var TILE='https://tile.openstreetmap.org/{z}/{x}/{y}.png';
var TS=256,MINZ=9,MAXZ=17;
var view={lat:G.center[0],lon:G.center[1],z:G.zoom||12},home=null;
var tilesEl=$('.tiles',box),svg=$('.ov',box),gEl=$('.ov g',box),mkEl=$('.mk',box),statEl=$('.mapstat',box),errEl=$('#maperr');
var layers={city:true,stations:true,districts:false,pois:false,sd:false};
var feats=[];      // {layer,rings:[[ [x,y] world-fraction ]],stroke,fill,dash,name,info,el}
var marks=[];      // {layer,lat,lon,cls,html,label,info,el}
var base={ox:0,oy:0,z:-1},dirty=true,cityBBox=null,cityRings=null;
var pal=['#1f6fb2','#d97706','#2e7d32','#8e24aa','#c62828','#00838f','#6d4c41','#3949ab','#ad1457','#558b2f','#ef6c00','#5d4037','#00695c','#4527a0','#9e9d24','#283593','#b71c1c','#37474f','#7b1fa2','#0277bd'];
var CAT={park:['公园与户外','#2e7d32'],trailhead:['步道与保护区入口','#558b2f'],library:['图书馆','#1565c0'],community:['社区与公共设施','#6a1b9a'],grocery:['超市与市集','#e65100'],shopping:['商业中心','#ad1457'],hospital:['医疗','#c62828'],school_admin:['学区与学校','#455a64']};

function frac(lat,lon){var r=lat*Math.PI/180;return [(lon+180)/360,(1-Math.log(Math.tan(r)+1/Math.cos(r))/Math.PI)/2]}
function unfrac(x,y){var n=Math.PI-2*Math.PI*y;return [180/Math.PI*Math.atan(0.5*(Math.exp(n)-Math.exp(-n))),x*360-180]}
function size(){return [box.clientWidth,box.clientHeight]}
function origin(){var s=TS*Math.pow(2,view.z),c=frac(view.lat,view.lon),wh=size();return [c[0]*s-wh[0]/2,c[1]*s-wh[1]/2,s]}

var tiles={},tileOK=0,tileBad=0;
function render(){
  var wh=size();if(!wh[0])return;
  var o=origin(),ox=Math.round(o[0]),oy=Math.round(o[1]),s=o[2],n=Math.pow(2,view.z),keep={};
  for(var tx=Math.floor(ox/TS);tx<=Math.floor((ox+wh[0])/TS);tx++){
    for(var ty=Math.floor(oy/TS);ty<=Math.floor((oy+wh[1])/TS);ty++){
      if(ty<0||ty>=n)continue;
      var k=view.z+'/'+(((tx%n)+n)%n)+'/'+ty+'@'+tx;keep[k]=1;
      var im=tiles[k];
      if(!im){im=new Image();im.alt='';im.draggable=false;
        im.onload=function(){tileOK++;this.style.opacity=1};
        im.onerror=function(){tileBad++;this.style.visibility='hidden';if(tileBad>=4&&!tileOK)fail('tiles')};
        im.style.opacity=0;im.style.transition='opacity .2s';
        im.src=TILE.replace('{z}',view.z).replace('{x}',((tx%n)+n)%n).replace('{y}',ty);
        tiles[k]=im;tilesEl.appendChild(im)}
      im.style.left=(tx*TS-ox)+'px';im.style.top=(ty*TS-oy)+'px';
    }
  }
  for(var key in tiles){if(!keep[key]){tilesEl.removeChild(tiles[key]);delete tiles[key]}}
  if(dirty||base.z!==view.z){base={ox:ox,oy:oy,z:view.z};dirty=false;
    feats.forEach(function(f){
      if(!f.el){f.el=document.createElementNS('http://www.w3.org/2000/svg','path');
        f.el.setAttribute('fill',f.fill||'none');f.el.setAttribute('fill-rule','evenodd');
        f.el.setAttribute('stroke',f.stroke);f.el.setAttribute('stroke-width',f.width||2);
        if(f.dash)f.el.setAttribute('stroke-dasharray',f.dash);
        if(f.fillOpacity!=null)f.el.setAttribute('fill-opacity',f.fillOpacity);
        f.el.setAttribute('stroke-linejoin','round');f.el._f=f;gEl.appendChild(f.el)}
      f.el.style.display=layers[f.layer]&&!f.off?'':'none';
      if(!layers[f.layer]||f.off)return;
      var d='';
      for(var i=0;i<f.rings.length;i++){var r=f.rings[i];
        for(var j=0;j<r.length;j++){d+=(j?'L':'M')+(r[j][0]*s-ox).toFixed(1)+' '+(r[j][1]*s-oy).toFixed(1)}
        d+='Z'}
      f.el.setAttribute('d',d);
    });
    marks.forEach(function(m){
      if(!m.el){m.el=document.createElement('button');m.el.type='button';m.el.className='mkr '+m.cls;m.el.innerHTML=m.html;
        m.el.setAttribute('aria-label',m.label);m.el.title=m.label;m.el._m=m;mkEl.appendChild(m.el)}
      m.el.style.display=layers[m.layer]?'':'none';
      var p=frac(m.lat,m.lon);m.el.style.left=(p[0]*s-ox)+'px';m.el.style.top=(p[1]*s-oy)+'px';
    });
  }
  var dx=base.ox-ox,dy=base.oy-oy;
  gEl.setAttribute('transform','translate('+dx+','+dy+')');
  mkEl.style.transform='translate('+dx+'px,'+dy+'px)';
  if(pop)placePop();
}
function redraw(){dirty=true;render()}
function setView(lat,lon,z){view.lat=Math.max(-85,Math.min(85,lat));view.lon=lon;view.z=Math.max(MINZ,Math.min(MAXZ,z));render()}
function zoomAt(dz,cx,cy){var nz=Math.max(MINZ,Math.min(MAXZ,view.z+dz));if(nz===view.z)return;
  var wh=size();if(cx==null){cx=wh[0]/2;cy=wh[1]/2}
  var o=origin(),fx=(o[0]+cx)/o[2],fy=(o[1]+cy)/o[2],s2=TS*Math.pow(2,nz);
  var c=unfrac((fx*s2-cx+wh[0]/2)/s2,(fy*s2-cy+wh[1]/2)/s2);setView(c[0],c[1],nz)}
function fit(bb,pad){var wh=size(),z=MAXZ;pad=pad||40;
  for(;z>MINZ;z--){var s=TS*Math.pow(2,z),a=frac(bb[3],bb[0]),b=frac(bb[1],bb[2]);
    if((b[0]-a[0])*s<=wh[0]-pad*2&&(b[1]-a[1])*s<=wh[1]-pad*2)break}
  setView((bb[1]+bb[3])/2,(bb[0]+bb[2])/2,z)}

/* 弹出信息 */
var pop=null;
function closePop(){if(pop){box.removeChild(pop.el);pop=null}}
function showPop(lat,lon,html){closePop();var el=document.createElement('div');el.className='mappop';
  el.innerHTML='<button class="x" type="button" aria-label="关闭">×</button>'+html;box.appendChild(el);
  el.querySelector('.x').onclick=function(e){e.stopPropagation();closePop()};
  ['pointerdown','click','dblclick'].forEach(function(t){el.addEventListener(t,function(e){e.stopPropagation()})});
  pop={el:el,lat:lat,lon:lon};placePop()}
function placePop(){var o=origin(),p=frac(pop.lat,pop.lon),wh=size();
  var x=p[0]*o[2]-Math.round(o[0]),y=p[1]*o[2]-Math.round(o[1]);
  pop.el.style.left=Math.max(130,Math.min(wh[0]-130,x))+'px';pop.el.style.top=Math.max(y,110)+'px'}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}

/* 交互 */
var ptrs={},drag=null,pinch=0;
function local(e){var r=box.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top]}
box.addEventListener('pointerdown',function(e){
  if(e.target.closest('.mapctl,.mappop,.maptap,.mapdone,.mapattr'))return;
  if(e.pointerType==='touch'&&!box.classList.contains('active'))return;
  if(e.button)return;
  ptrs[e.pointerId]=local(e);
  var ids=Object.keys(ptrs);
  if(ids.length===1){drag={x:e.clientX,y:e.clientY,moved:0,t:e.target,o:origin()};}
  else if(ids.length===2){var a=ptrs[ids[0]],b=ptrs[ids[1]];pinch=Math.hypot(a[0]-b[0],a[1]-b[1]);drag=null}
  try{box.setPointerCapture(e.pointerId)}catch(_){}
});
box.addEventListener('pointermove',function(e){
  if(!(e.pointerId in ptrs))return;
  ptrs[e.pointerId]=local(e);var ids=Object.keys(ptrs);
  if(ids.length===2&&pinch){var a=ptrs[ids[0]],b=ptrs[ids[1]],d=Math.hypot(a[0]-b[0],a[1]-b[1]);
    if(d>pinch*1.45){zoomAt(1,(a[0]+b[0])/2,(a[1]+b[1])/2);pinch=d}else if(d<pinch*0.69){zoomAt(-1,(a[0]+b[0])/2,(a[1]+b[1])/2);pinch=d}
    return}
  if(!drag)return;
  var dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.moved=Math.max(drag.moved,Math.abs(dx)+Math.abs(dy));
  if(drag.moved<4)return;
  box.classList.add('drag');
  var s=drag.o[2],wh=size(),c=unfrac((drag.o[0]-dx+wh[0]/2)/s,(drag.o[1]-dy+wh[1]/2)/s);
  view.lat=c[0];view.lon=c[1];render();
});
function up(e){
  if(!(e.pointerId in ptrs))return;
  delete ptrs[e.pointerId];pinch=0;box.classList.remove('drag');
  if(drag&&drag.moved<4&&e.type==='pointerup')tap(drag.t,local(e));
  drag=null;
}
box.addEventListener('pointerup',up);box.addEventListener('pointercancel',up);
function tap(t,xy){
  var b=t.closest&&t.closest('.mkr');
  if(b&&b._m){var m=b._m;if(m.go){var el=document.getElementById(m.go);if(el){if(el.tagName==='DETAILS')el.open=true;el.scrollIntoView()}return}
    showPop(m.lat,m.lon,m.info);return}
  if(t._f&&t._f.info){var o=origin(),c=unfrac((o[0]+xy[0])/o[2],(o[1]+xy[1])/o[2]);showPop(c[0],c[1],t._f.info);return}
  closePop();
}
box.addEventListener('dblclick',function(e){if(e.target.closest('.mapctl,.mappop,.mkr'))return;var p=local(e);zoomAt(1,p[0],p[1])});
box.addEventListener('wheel',function(e){if(!(e.ctrlKey||e.metaKey))return;e.preventDefault();var p=local(e);zoomAt(e.deltaY<0?1:-1,p[0],p[1])},{passive:false});
$('.zin',box).onclick=function(){zoomAt(1)};$('.zout',box).onclick=function(){zoomAt(-1)};
$('.zhome',box).onclick=function(){closePop();if(home)fit(home);else setView(G.center[0],G.center[1],G.zoom||12)};
var tapBtn=$('.maptap',box),doneBtn=$('.mapdone',box);
if(tapBtn)tapBtn.onclick=function(){box.classList.add('active')};
if(doneBtn)doneBtn.onclick=function(){box.classList.remove('active')};
window.addEventListener('resize',function(){redraw()});

/* 读取官方服务（先 CORS，失败时 JSONP） */
var cbn=0;
function qs(p){return Object.keys(p).map(function(k){return encodeURIComponent(k)+'='+encodeURIComponent(p[k])}).join('&')}
function jsonp(url,p,cbParam){return new Promise(function(res,rej){var name='__jcmap'+(++cbn),sc=document.createElement('script'),done=false;
  var t=setTimeout(function(){fin();rej(new Error('timeout'))},20000);
  function fin(){done=true;clearTimeout(t);try{delete window[name]}catch(_){window[name]=undefined}if(sc.parentNode)sc.parentNode.removeChild(sc)}
  window[name]=function(d){if(done)return;fin();res(d)};
  var q={};for(var k in p)q[k]=p[k];q[cbParam||'callback']=name;
  sc.onerror=function(){if(done)return;fin();rej(new Error('load'))};sc.src=url+'?'+qs(q);document.head.appendChild(sc)})}
function getJSON(url,p,jp){
  var ctl=('AbortController' in window)?new AbortController():null,t=ctl&&setTimeout(function(){ctl.abort()},15000);
  return fetch(url+'?'+qs(p),ctl?{signal:ctl.signal}:{}).then(function(r){if(t)clearTimeout(t);if(!r.ok)throw new Error(r.status);return r.json()})
    .catch(function(){var q={};for(var k in p)q[k]=p[k];if(jp)for(var j in jp)q[j]=jp[j];return jsonp(url,q)})}
function cacheGet(k,maxAgeH){try{var v=JSON.parse(localStorage.getItem(k));if(v&&Date.now()-v.t<maxAgeH*36e5)return v.d}catch(_){}return undefined}
function cacheSet(k,d){try{localStorage.setItem(k,JSON.stringify({t:Date.now(),d:d}))}catch(_){}}
var svcLayers={};
function layerId(svc,name,fallback){
  if(!svcLayers[svc])svcLayers[svc]=getJSON(TIGER+svc+'/MapServer',{f:'json'}).catch(function(){return {}});
  return svcLayers[svc].then(function(d){var ls=(d&&d.layers)||[];for(var i=0;i<ls.length;i++){if(ls[i].name===name&&!ls[i].subLayerIds)return ls[i].id}return fallback})}
function toRings(geom){return ((geom&&geom.rings)||[]).map(function(r){return r.map(function(p){return frac(p[1],p[0])})})}
function bboxOf(geom){var b=[180,90,-180,-90];(geom.rings||[]).forEach(function(r){r.forEach(function(p){if(p[0]<b[0])b[0]=p[0];if(p[0]>b[2])b[2]=p[0];if(p[1]<b[1])b[1]=p[1];if(p[1]>b[3])b[3]=p[1]})});return b}
function inRings(rings,x,y){var c=false;for(var i=0;i<rings.length;i++){var r=rings[i];for(var a=0,b=r.length-1;a<r.length;b=a++){
  if((r[a][1]>y)!==(r[b][1]>y)&&x<(r[b][0]-r[a][0])*(y-r[a][1])/(r[b][1]-r[a][1])+r[a][0])c=!c}}return c}
function stat(t){statEl.textContent=t||''}
var failed={};
function osmLink(){return 'https://www.openstreetmap.org/#map='+view.z+'/'+view.lat.toFixed(4)+'/'+view.lon.toFixed(4)}
function fail(what){if(failed[what])return;failed[what]=1;
  var msg={tiles:'底图暂时未能加载。可以直接在地图网站打开这一位置：<a target="_blank" rel="noopener" href="'+osmLink()+'">打开 OpenStreetMap ↗</a>',
    city:'城市边界图层暂时未能从 U.S. Census Bureau 读取，可稍后刷新页面，或打开官方地图：<a target="_blank" rel="noopener" href="https://tigerweb.geo.census.gov/tigerweb/">Census TIGERweb 地图 ↗</a>',
    sd:'学区范围图层暂时未能从 U.S. Census Bureau 读取。请直接使用本栏各学区的官方地址查询入口。'}[what];
  if(errEl&&msg){var d=document.createElement('div');d.innerHTML=msg;errEl.appendChild(d);errEl.hidden=false}
  if(what==='tiles'&&!$('.mapfall',box)){var f=document.createElement('div');f.className='mapfall';
    f.innerHTML='<button class="x" type="button" aria-label="关闭">×</button><p><b>地图底图暂时未能加载</b>'+esc(G.name)+' 的位置可以在下面的地图网站查看；学校、路线和环境查询请用右侧的官方入口。</p><p><a class="btn sm solid" target="_blank" rel="noopener" href="'+osmLink()+'">在 OpenStreetMap 打开 ↗</a> <a class="btn sm" target="_blank" rel="noopener" href="'+gmaps(G.name+', CA')+'">在 Google 地图打开 ↗</a></p>';
    ['pointerdown','click','dblclick'].forEach(function(t){f.addEventListener(t,function(e){e.stopPropagation()})});f.querySelector('.x').onclick=function(){box.removeChild(f)};box.appendChild(f)}}

function loadCity(){
  var ck='jcmap:city:'+G.slug,c=cacheGet(ck,24*14);
  var p=c?Promise.resolve(c):layerId('Places_CouSub_ConCity_SubMCD','Incorporated Places',4).then(function(id){
    return getJSON(TIGER+'Places_CouSub_ConCity_SubMCD/MapServer/'+id+'/query',{where:"STATE='06' AND BASENAME='"+G.name+"'",outFields:'NAME,BASENAME,GEOID',returnGeometry:'true',outSR:4326,geometryPrecision:5,maxAllowableOffset:0.00012,f:'json'})
  }).then(function(d){if(!d||!d.features||!d.features.length)throw new Error('empty');var g=d.features[0].geometry;if(!g||!g.rings||!g.rings.length)throw new Error('geom');cacheSet(ck,g);return g});
  stat('正在读取城市边界…');
  return p.then(function(g){
    cityBBox=bboxOf(g);cityRings=g.rings;home=cityBBox;
    feats.push({layer:'city',rings:toRings(g),stroke:'#102445',width:2.6,fill:'#c6a35b',fillOpacity:0.10,
      info:'<b>'+esc(G.name)+' 城市边界</b>来源：U.S. Census Bureau TIGERweb 现行 Incorporated Places 图层。邮寄地址写 '+esc(G.name)+' 的房屋不一定在市界内。'});
    stat('');fit(cityBBox);redraw();
    var el=$('#mapdate');if(el)el.textContent='本次读取：'+new Date().toLocaleDateString('zh-CN');
  }).catch(function(){stat('');fail('city')});
}

/* 学区范围 */
var sdLoaded=null;
function norm(s,deep){s=s.toLowerCase().normalize?s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,''):s.toLowerCase();
  s=s.replace(/[-–—\/]/g,' ').replace(/\b(school|district|elementary|joint|the|of)\b/g,' ');
  if(deep)s=s.replace(/\b(union|unified|city)\b/g,' ');return s.replace(/[^a-z ]/g,'').replace(/\s+/g,' ').trim()}
function matchSD(name){var a=norm(name),b=norm(name,true),list=G.sd||[],i;
  for(i=0;i<list.length;i++)if(norm(list[i].name)===a)return list[i];
  for(i=0;i<list.length;i++)if(norm(list[i].name,true)===b)return list[i];return null}
function loadSD(){
  if(sdLoaded)return sdLoaded;
  var lg=$('#sdlegend');if(lg)lg.innerHTML='<li>正在读取学区范围…</li>';
  var kinds=[['Unified School Districts','联合学区（小学至高中）',0],['Elementary School Districts','小学／初中学区',2],['Secondary School Districts','高中学区',1]];
  var ready=cityBBox?Promise.resolve():Promise.reject(new Error('nocity'));
  sdLoaded=ready.then(function(){
    var bb=cityBBox,pts=[],N=44,i,j;
    for(i=0;i<N;i++)for(j=0;j<N;j++){var x=bb[0]+(bb[2]-bb[0])*(i+.5)/N,y=bb[1]+(bb[3]-bb[1])*(j+.5)/N;if(inRings(cityRings,x,y))pts.push([x,y])}
    return Promise.all(kinds.map(function(k){return layerId('School',k[0],k[2]).then(function(id){
      return getJSON(TIGER+'School/MapServer/'+id+'/query',{geometry:bb.join(','),geometryType:'esriGeometryEnvelope',inSR:4326,spatialRel:'esriSpatialRelIntersects',outFields:'NAME,GEOID',returnGeometry:'true',outSR:4326,geometryPrecision:5,maxAllowableOffset:0.0003,f:'json'})
    }).then(function(d){return ((d&&d.features)||[]).map(function(f){return {name:f.attributes.NAME,kind:k[1],sec:k[2]===1,geom:f.geometry}})})})).then(function(rs){
      var all=[].concat.apply([],rs),out=[],need=Math.max(2,Math.round(pts.length*0.0025));
      all.forEach(function(d){if(!d.geom||!d.geom.rings)return;var n=0;for(var q=0;q<pts.length;q++){if(inRings(d.geom.rings,pts[q][0],pts[q][1]))n++}
        if(n>=need){d.share=n/pts.length;out.push(d)}});
      if(!out.length)throw new Error('none');
      out.sort(function(a,b){return (a.sec-b.sec)||(b.share-a.share)});
      if(lg)lg.innerHTML='';
      out.forEach(function(d,ix){var col=pal[ix%pal.length],m=matchSD(d.name);
        var info='<b>'+esc(d.name)+'</b>'+d.kind+'。这是学区范围，不是具体学校的招生范围。'+(m&&m.url?'<br><a target="_blank" rel="noopener" href="'+esc(m.url)+'">按地址查询学校 ↗</a>':'');
        var f={layer:'sd',rings:toRings(d.geom),stroke:col,width:d.sec?2.6:1.6,dash:d.sec?'7 5':null,fill:d.sec?'none':col,fillOpacity:d.sec?null:0.16,info:info};
        feats.push(f);
        if(lg){var li=document.createElement('li');
          li.innerHTML='<label><input type="checkbox" checked><span class="sw'+(d.sec?' dash':'')+'" style="border-color:'+col+(d.sec?'':';background:'+col+'33')+'"></span><span>'+esc(d.name)+'<br><small class="small">'+d.kind+(m&&m.url?' · <a target="_blank" rel="noopener" href="'+esc(m.url)+'">按地址查询 ↗</a>':'')+'</small></span></label>';
          li.querySelector('input').onchange=function(){f.off=!this.checked;redraw()};lg.appendChild(li)}
      });
      redraw();
    })
  }).catch(function(){if(lg)lg.innerHTML='';fail('sd')});
  return sdLoaded;
}

/* 地点定位 */
var gq=[],gbusy=0;
function okPoint(lat,lon){var bb=cityBBox||[G.center[1]-.3,G.center[0]-.3,G.center[1]+.3,G.center[0]+.3],pad=0.16;
  return lon>bb[0]-pad&&lon<bb[2]+pad&&lat>bb[1]-pad&&lat<bb[3]+pad}
function geocode(addr){return new Promise(function(res){gq.push([addr,res]);pump()})}
function pump(){while(gbusy<2&&gq.length){(function(job){gbusy++;
  var k='jcmap:geo:'+job[0],c=cacheGet(k,24*60);
  var p=(c!==undefined)?Promise.resolve(c):getJSON(GEOCODER,{address:job[0],benchmark:'Public_AR_Current',format:'json'},{format:'jsonp'}).then(function(d){
      var m=d&&d.result&&d.result.addressMatches&&d.result.addressMatches[0],v=m&&m.coordinates?[+m.coordinates.y,+m.coordinates.x]:null;cacheSet(k,v);return v}).catch(function(){return null});
  p.then(function(v){gbusy--;job[1](v&&okPoint(v[0],v[1])?v:null);pump()})})(gq.shift())}}
var pointsStarted={};
function gmaps(q){return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(q)}
function addPoints(kind){
  if(pointsStarted[kind])return;pointsStarted[kind]=1;
  if(kind==='stations')(G.stations||[]).forEach(function(s){if(!s.a)return;geocode(s.a).then(function(v){if(!v)return;
    marks.push({layer:'stations',lat:v[0],lon:v[1],cls:'st',html:'<i></i>',label:s.n,info:'<b>'+esc(s.n)+'</b>'+esc(s.sys)+'<br>'+esc(s.a)+'<br><a target="_blank" rel="noopener" href="'+gmaps(s.n+' station, '+s.a)+'">在地图应用中打开 ↗</a>'});redraw()})});
  if(kind==='pois')(G.pois||[]).forEach(function(p){if(!p.a)return;geocode(p.a).then(function(v){if(!v)return;var c=CAT[p.c]||['地点','#455a64'];
    marks.push({layer:'pois',lat:v[0],lon:v[1],cls:'poi',html:'<i style="background:'+c[1]+'"></i>',label:p.n,info:'<b>'+esc(p.n)+'</b>'+c[0]+(p.d?' · '+esc(p.d):'')+'<br>'+esc(p.a)+'<br><a target="_blank" rel="noopener" href="'+gmaps(p.n+', '+p.a)+'">在地图应用中打开 ↗</a>'});redraw()})});
  if(kind==='districts')(G.districts||[]).forEach(function(d){if(!d.a)return;geocode(d.a).then(function(v){if(!v)return;
    marks.push({layer:'districts',lat:v[0],lon:v[1],cls:'dl',html:esc(d.s||d.n),label:d.n+'（片区代表点，非边界）',go:d.id});redraw()})});
}

/* 图层切换 */
var presets={locate:{city:1,stations:1},life:{city:1,districts:1,pois:1},school:{city:1,sd:1},routes:{city:1,stations:1},env:{city:1}};
function setTab(id){
  $$('.maptabs button').forEach(function(b){b.setAttribute('aria-selected',b.dataset.tab===id?'true':'false')});
  $$('.mapside .pane').forEach(function(p){p.hidden=p.dataset.pane!==id});
  var p=presets[id]||presets.locate;for(var k in layers)layers[k]=!!p[k];
  closePop();
  if(started){if(layers.stations)addPoints('stations');if(layers.pois)addPoints('pois');if(layers.districts)addPoints('districts');if(layers.sd)cityReady.then(loadSD)}
  redraw();
}
$$('.maptabs button').forEach(function(b){b.onclick=function(){setTab(b.dataset.tab)}});
var started=false,cityReady=null,curTab='locate';
function start(){if(started)return;started=true;render();cityReady=loadCity();
  var cur=$('.maptabs button[aria-selected=true]');setTab(cur?cur.dataset.tab:'locate')}
if('IntersectionObserver' in window){var mo=new IntersectionObserver(function(es){if(es[0].isIntersecting){mo.disconnect();start()}},{rootMargin:'600px'});mo.observe(box)}else start();
})();
