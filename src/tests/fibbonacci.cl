class A
{};
class B inherits A
{};
class C inherits B
{};
class D inherits C
{};

class Main inherits IO
{
	main():Object
	{
		out_int(fibb(in_int()))
	};
	
	fibb(n: Int):Int
	{
	 {
		if (n=1) then 1 else 
		{
			if (n=2) then 1 else fibb(n-1)+fibb(n-2) fi;
		}
		fi;
	 }
	};
};