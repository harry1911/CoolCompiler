class Main inherits IO {
    g() : Int { 1 };
    f(x:Int):Int { if x=0 then g() else f(x- 1) fi };
    main() : Object {out_int(f(3))};
};
