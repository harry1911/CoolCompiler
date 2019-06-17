class Count {
    i : Int <- 0;
    inc() : SELF_TYPE {
        {
            i <- i + 1;
            self;
        }
    };
};

class Stock inherits Count {
    name : String; -- name of item
    x : SELF_TYPE <- new SELF_TYPE;
    name() : String {
        name
    };
};

class Main {
    a : Stock <- (new Stock).inc();

    main() : Object {
        a.inc()
    };
};
