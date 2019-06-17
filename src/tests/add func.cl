class Main inherits IO 
{
    y: Int <- 10;
	
  add(x: Int, z:Int): Int 
	{
		{
			x+y+z;
		} 
	};
    main(): Object
	{
        {
            out_int(add(4, 3));  
        }
    };    
};
