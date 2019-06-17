class Main inherits IO 
{   
	y: Int <- 10;
	
	bucle(to: Int): Int
	{
		let acumul : Int <- 0 in
		{
			y <- 0;
			while (y < to) loop 
			{
				acumul <- acumul + y;
				y <- y + 1;
			}
			pool;
			acumul;
		}
	};	
	
    main(): Object
	{
		let var: B <- new B in var@Utils.test(12)
    };    
};

class Utils
{
	y: Int <- 10;
	
    add(x: Int, z:Int): Int 
	{
		{
			x + resta(y,z);
		} 
	};
	
	resta(x: Int, y: Int): Int
	{
		x-y
	};
	
	test(val: Int): Bool
	{
		if val < 10 then true else false fi
	};
};

class B inherits Utils
{
	test(val: Int): Bool
	{
		if val < 15 then true else false fi
	};
};
