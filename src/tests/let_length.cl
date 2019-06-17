class Main inherits IO {
    y : String <- "abba";
    z : Int <- 2;

    main() : Object {
      out_int(let x : Int <- y.length() in x+z)
    };
};
