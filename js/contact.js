(function(){
  var API="https://epicstack-assistant.onrender.com",f=document.getElementById("enq"),s=document.getElementById("status"),t0=Date.now();
  fetch(API+"/health",{mode:"no-cors"}).catch(function(){});
  if(!f)return;
  function say(m,c){s.textContent=m;s.className="status "+(c||"")}
  f.addEventListener("submit",function(ev){
    ev.preventDefault();
    if(!f.checkValidity()){f.reportValidity();return}
    var b=f.querySelector("button"),d=Object.fromEntries(new FormData(f));
    d.elapsed=(Date.now()-t0)/1000;
    b.disabled=true;say("Sending…");
    var slow=setTimeout(function(){say("Still sending. Our server is waking up, which can take up to a minute.")},5000);
    var ctl=new AbortController(),to=setTimeout(function(){ctl.abort()},80000);
    fetch(API+"/enquiry",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d),signal:ctl.signal})
    .then(function(r){return r.json().catch(function(){return{}}).then(function(j){return{st:r.status,j:j}})})
    .then(function(x){
      if(x.st===200&&x.j.ok){f.hidden=true;document.getElementById("thanks").hidden=false;say("");return}
      b.disabled=false;
      if(x.st===429)say("Too many enquiries from your connection. Please try again later.","err");
      else if(x.st===422||x.st===400)say("Please check your name, email, phone number and message (at least 10 characters).","err");
      else say("Something went wrong on our side. Please try again in a minute.","err");
    }).catch(function(){b.disabled=false;say("We couldn’t send your enquiry. Please check your connection and try again.","err")})
    .then(function(){clearTimeout(slow);clearTimeout(to)});
  });
})();
