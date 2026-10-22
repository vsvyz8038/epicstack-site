(function(){
  var b=document.querySelector(".burger"),n=document.getElementById("menu");
  if(b&&n){b.addEventListener("click",function(){var o=n.classList.toggle("open");b.setAttribute("aria-expanded",o)});}
  var y=document.getElementById("y");if(y)y.textContent=new Date().getFullYear();
  var calm=window.matchMedia&&matchMedia("(prefers-reduced-motion:reduce)").matches;
  if(!("IntersectionObserver" in window)||calm)return;
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}})},{threshold:.15});
  document.querySelectorAll(".row,.demo,.band,.flow,.sec>h2").forEach(function(el,i){
    if(!el.classList.contains("flow")){el.classList.add("rv");el.style.transitionDelay=((i%4)*80)+"ms"}
    el.classList.add("pre");io.observe(el);
  });
})();
