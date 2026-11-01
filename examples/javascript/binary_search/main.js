function f(a,t){let l=0,r=a.length-1;while(l<=r){let m=(l+r)>>1;if(a[m]===t)return m;if(a[m]<t)l=m+1;else r=m-1;}return -1;}
if(f([1,3,5],5)!==2||f([],1)!==-1||f([1],1)!==0)throw Error("failed");
