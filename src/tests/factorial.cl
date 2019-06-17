class Main inherits IO {
    main():Object{
      {
        out_int(iterative(5));
        out_string("\n");
        out_int(fact(5));
        out_string("\n");
      }
    };
    fact(i:Int):Int{
        if (i=1) then 1 else i*fact(i-1) fi
    };
    iterative(i:Int):Int{
        let f:Int<-1 in 
            {
                while(not(i=0)) loop
                    {
                        f<-f*i;
                        i<-i-1;
                    }   
                pool;
                f;
            }
    };
};
