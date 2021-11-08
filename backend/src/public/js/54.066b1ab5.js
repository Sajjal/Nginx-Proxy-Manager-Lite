"use strict";(self["webpackChunknpmlite"]=self["webpackChunknpmlite"]||[]).push([[54],{5041:(e,a,s)=>{s.d(a,{Z:()=>u});var r=s(1959),t=s(52),n=s.n(t),o=s(9582),l=s(4584);const i=()=>{const e=(0,r.iH)(null),a="/",s=(0,o.tv)();function t(e){const a=`; ${document.cookie}`,s=a.split(`; ${e}=`);if(2===s.length)return s.pop().split(";").shift()}const i={withCredentials:!0,credentials:"same-origin",headers:{"X-CSRF-TOKEN":t("csrf_access_token")}},u=async r=>{try{const t=await n().post(`${a}login`,r,i);if(e.value=null,"Change Password"!==t.data.Status)return s.push({name:"Dashboard"});if("Change Password"==t.data.Status)return l["default"].dispatch("update_change_password",{change:!0,afterLogin:!1})}catch(t){e.value=t.response.data.Error}},d=async r=>{try{return await n().post(`${a}changePassword`,r,i),s.push({name:"Dashboard"})}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},c=async r=>{try{return await n().post(`${a}changePasswordLater`,r,i),s.push({name:"Dashboard"})}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},p=async r=>{try{const s=await n().post(`${a}create`,r,i);return e.value=null,l["default"].dispatch("add_to_domain_list",r),s.data}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},w=async r=>{try{return await n().post(`${a}update`,r,i),e.value=null,await v(),void await h()}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},m=async r=>{try{const s=await n().post(`${a}requestSSL`,r,i);return e.value=null,s.data}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},v=async()=>{try{const s=await n().get(`${a}list`,i);return l["default"].dispatch("update_domain_list",s.data.domain_list),void(e.value=null)}catch(r){if(e.value=r.response.data.Error,r.response&&401==r.response.status)return s.push({name:"Login"})}},h=async()=>{try{const s=await n().get(`${a}listSSL`,i);return l["default"].dispatch("update_ssl_list",s.data.ssl_list),void(e.value=null)}catch(r){if(e.value=r.response.data.Error,r.response&&401==r.response.status)return s.push({name:"Login"})}},g=async r=>{try{return await n().post(`${a}delete`,r,i),await v(),await h(),void(e.value=null)}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},f=async r=>{try{return await n().post(`${a}enable`,r,i),await v(),void(e.value=null)}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},y=async r=>{try{return await n().post(`${a}disable`,r,i),await v(),void(e.value=null)}catch(t){if(e.value=t.response.data.Error,t.response&&401==t.response.status)return s.push({name:"Login"})}},_=async e=>{try{return await n().post(`${a}logout`,e,i),s.push({name:"Login"})}catch(r){return s.push({name:"Login"})}};return{error:e,login:u,logout:_,changePassword:d,changePasswordLater:c,addNewHost:p,updateHost:w,requestNewSSL:m,listHosts:v,enableHost:f,disableHost:y,deleteHost:g,listSSLCerts:h}},u=i},6054:(e,a,s)=>{s.r(a),s.d(a,{default:()=>$});var r=s(3673),t=s(8880),n=s(2323);const o=(0,r._)("span",{class:"text-h6",style:{cursor:"default"}}," Nginx Proxy Manager Lite ",-1),l={key:0,class:"text-h6 text-black flex flex-center",style:{cursor:"default"}},i={class:"q-pa-md"},u={key:1,class:"q-mt-md q-pa-sm bg-negative text-white",style:{"font-size":"18px",cursor:"default"}};function d(e,a,s,d,c,p){const w=(0,r.up)("q-icon"),m=(0,r.up)("q-banner"),v=(0,r.up)("q-card-section"),h=(0,r.up)("q-separator"),g=(0,r.up)("q-input"),f=(0,r.up)("q-btn"),y=(0,r.up)("q-btn-group"),_=(0,r.up)("q-card-actions"),L=(0,r.up)("q-card"),q=(0,r.up)("q-page");return(0,r.wg)(),(0,r.j4)(q,{class:"flex flex-center"},{default:(0,r.w5)((()=>[(0,r.Wm)(L,{class:"my-card",style:{width:"400px"}},{default:(0,r.w5)((()=>[(0,r.Wm)(v,null,{default:(0,r.w5)((()=>[(0,r.Wm)(m,{"inline-actions":"",rounded:"",class:"text-white bg-primary text-center",style:{overflow:"hidden"}},{default:(0,r.w5)((()=>[(0,r.Wm)(w,{name:"settings_input_antenna",class:"q-mr-sm",size:"md"}),o])),_:1})])),_:1}),(0,r.Wm)(h),e.store.state.change_password.change?((0,r.wg)(),(0,r.iD)("p",l,"Change Account Info!")):(0,r.kq)("",!0),(0,r.Wm)(_,{vertical:""},{default:(0,r.w5)((()=>[(0,r._)("div",i,[(0,r.Wm)(g,{filled:"",modelValue:e.email,"onUpdate:modelValue":a[0]||(a[0]=a=>e.email=a),label:"Email"},{append:(0,r.w5)((()=>[(0,r.Wm)(w,{name:"mail"})])),_:1},8,["modelValue"]),(0,r.Wm)(g,{modelValue:e.password,"onUpdate:modelValue":a[2]||(a[2]=a=>e.password=a),filled:"",type:e.isPwd?"password":"text",label:"Password",class:"q-mt-md",onKeyup:(0,t.D2)(e.userLogin,["enter"])},{append:(0,r.w5)((()=>[(0,r.Wm)(w,{name:e.isPwd?"visibility_off":"visibility",class:"cursor-pointer",onClick:a[1]||(a[1]=a=>e.isPwd=!e.isPwd)},null,8,["name"])])),_:1},8,["modelValue","type","onKeyup"]),e.store.state.change_password.change?((0,r.wg)(),(0,r.j4)(g,{key:0,modelValue:e.verify_password,"onUpdate:modelValue":a[4]||(a[4]=a=>e.verify_password=a),filled:"",type:e.isPwd?"password":"text",label:"Confirm Password",class:"q-mt-md",onKeyup:(0,t.D2)(e.userLogin,["enter"])},{append:(0,r.w5)((()=>[(0,r.Wm)(w,{name:e.isPwd?"visibility_off":"visibility",class:"cursor-pointer",onClick:a[3]||(a[3]=a=>e.isPwd=!e.isPwd)},null,8,["name"])])),_:1},8,["modelValue","type","onKeyup"])):(0,r.kq)("",!0),e.error?((0,r.wg)(),(0,r.iD)("div",u,[(0,r.Wm)(w,{name:"error",class:"text-white q-mr-sm",size:"md"}),(0,r.Uk)(" "+(0,n.zw)(e.error),1)])):(0,r.kq)("",!0),(0,r.Wm)(y,{spread:"",class:"q-mt-md"},{default:(0,r.w5)((()=>[e.store.state.change_password.change?((0,r.wg)(),(0,r.j4)(f,{key:0,color:"primary",label:"Update",icon:"send",onClick:e.changeUserPassword},null,8,["onClick"])):((0,r.wg)(),(0,r.j4)(f,{key:1,color:"primary",label:"Login",icon:"send",onClick:e.userLogin},null,8,["onClick"])),(0,r.Wm)(f,{color:"grey",label:"Clear",icon:"clear",onClick:e.clearLoginForm},null,8,["onClick"])])),_:1})])])),_:1})])),_:1})])),_:1})}var c=s(1959),p=s(4584),w=s(5041);const m=(0,r.aZ)({name:"Login",setup(){const e=(0,c.iH)(null),a=(0,c.iH)(null),s=(0,c.iH)(null),r=/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,{error:t,login:n,changePassword:o,changePasswordLater:l}=(0,w.Z)();async function i(){return e.value?a.value?e.value.match(r)?void await n({email:e.value,password:a.value}):t.value="Error: Invalid Email provided!":t.value="Error: Password is required!":t.value="Error: Email is required!"}async function u(){return e.value?a.value?a.value.length<10?t.value="Password must be >10 characters!":a.value!=s.value?t.value="Error: Password does not match!":e.value.match(r)?(p["default"].state.change_password.afterLogin||await o({email:e.value,password:a.value}),p["default"].state.change_password.afterLogin&&await l({email:e.value,password:a.value}),t.value?void 0:p["default"].dispatch("update_change_password",!1)):t.value="Error: Invalid Email provided!":t.value="Error: Password is required!":t.value="Error: Email is required!"}function d(){e.value=a.value=s.value=t.value=null}return{store:p["default"],password:a,verify_password:s,email:e,isPwd:(0,c.iH)(!0),error:t,userLogin:i,changeUserPassword:u,clearLoginForm:d}}});var v=s(4260),h=s(4379),g=s(151),f=s(5589),y=s(5607),_=s(4554),L=s(5869),q=s(9367),P=s(4842),b=s(6375),k=s(8240),E=s(7518),C=s.n(E);const x=(0,v.Z)(m,[["render",d]]),$=x;C()(m,"components",{QPage:h.Z,QCard:g.Z,QCardSection:f.Z,QBanner:y.Z,QIcon:_.Z,QSeparator:L.Z,QCardActions:q.Z,QInput:P.Z,QBtnGroup:b.Z,QBtn:k.Z})}}]);