class Main inherits IO 
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
	
    main(): Object
	{
        {
            test(14);  
        }
    };    
};
