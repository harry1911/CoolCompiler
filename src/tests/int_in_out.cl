class Main inherits IO 
{   	
    main(): Object
	{
		{
		    let a:Int <- in_int() in {
				out_string("You wrote: ");
				out_int(a); 
				out_string("\n");
			};
		}
    };    
};