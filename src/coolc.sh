
# Incluya aquí las instrucciones necesarias para ejecutar su compilador

# INPUT_FILE=$1
# OUTPUT_FILE=${INPUT_FILE:0: -2}mips

# Si su compilador no lo hace ya, aquí puede imprimir la información de contacto
echo "COOL Compiler Version 1.0 of June 13, 2019."   # Recuerde cambiar estas
echo "Copyright (c) 2019 School of Math and Computer Science, University of Havana: Hector, Frankie and Frank."    # líneas a los valores correctos

# Llamar al compilador
# echo "Compiling $INPUT_FILE into $OUTPUT_FILE"

python3 coolc.py $@
