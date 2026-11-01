function f(s){s=s.toLowerCase().replace(/[^a-z0-9]/g,"");return s===s.split("").reverse().join("");}
if(!f("A man, a plan, a canal: Panama")||f("abc")||!f(""))throw Error("failed");
