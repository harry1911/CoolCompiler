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
		case (new B) of 
			-- x:A => out_string("class A");
			-- x:B => out_string("class B");
			x:C => out_string("class C");
			x:D => out_string("class D");
			-- x:Object => out_string("class Object");
		esac
	};
};