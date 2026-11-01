function f(a,b){a=Math.abs(a);b=Math.abs(b);while(b){[a,b]=[b,a%b];}return a;}
if(f(-12,18)!==6||f(0,0)!==0||f(7,0)!==7)throw Error("failed");
