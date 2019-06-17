class Crash {
};

class Brash inherits Crash{
	dl(hl : Brash) : Int {
		1
	};
};

class Main inherits IO {
	main() : Object {
			{
					out_string("Enter number of numbers to multiply\n");
					out_int(prod(in_int()));
					out_string("\n");
					case (new Crash) of
						l : Brash => (new Brash); -- case type reused.
						f : Crash => out_int((new Brash).dl(new Brash));
					esac;
			}
	};

	prod(i : Int) : Int {
		let y : Int <- 1 in {
				while (not(i <= 0 )) loop {
						out_string("Enter Number: ");
						y <- y * in_int();
						i <- i - 1;
				}
				pool;
				y;
		}
	};
};
