class Main inherits IO 
{
    y: Int <- 10;
	acumul: Int <- 0;
	
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
		if val = 10 then true else false fi
	};
	
	bucle(to: Int): Int
	{
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
        {
            bucle(10);  
        }
    };    
};
