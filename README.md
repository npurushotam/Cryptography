# Cryptography
A cascaded cryptography system based on an idea of using armstrong numbers and matrices for encryption/decryption which was published in a research paper. 

In this program the basic idea is that user will provide a key based on that key file will get encrypted and same key must be used to decrypt the file. During encryption and decryption original file is divided into many chunks and process of encryption/decryption is done simultaneously which is achived by use of multithreading.

### How file is processed during encryption/decryption
1. To process file there are two classes in the program named FileProcessor and ChunkProcessor. 
2. FileProcessor class takes in the file and divided it into N (8 in our case) chunks.
3. Each of these chunks are given to ChunkProcessor class along with key and command for encryption/decryption.
4. Then in the constructor of this class for the process of encryption/decryption new thread gets created and activated.
5. Each chunk gets processed byte by byte and gets stored in a target file, which in the end gets merged in the FileProcessor class.
6. After merging and getting final encrypted/decrypted file, target files for each chunk created earlier gets deleted using ```os.remove()```.

### How encryption and decryption of file is done
1. The user provides a _key_ using it a XOR value is generated and base value of 3 matrices is generated.
2. The matrix is _16 * 16_ matrix which has 256 elements and is used to store 1 byte of data.
4. Now lets say the base values for 3 matrices is (24, 210, 231). Further the base values is  incremented sequentially and in a cyclic manner to fill up the matrix elements, as follows:
```
Matrix-1 : 24, 25, 26, ..., 255, 0, 1, 2, 3, ... 23

Matrix-2 : 210, 211, 212, ..., 255, 0, 1, 2, 3, ... 209

Matrix-3 : 231, 232, 233, ..., 255, 0, 1, 2, 3, ... 230
```

4. During encryption, Data (byte) to be encrypted is splitted into 2 nibbles. The higher nibble acts as row and lower one as column. By using this row, col as co-ordinates we get encoded value from matrix.
5. During decryption, the encoded value which is unique is to be searched in the matrix and co-ordinates (row, col) of matching element are to be treated as the high nibble and lower nibble from which we get original data back.
6. Also instead of creating an actual matrix, we simply use mathematical formula to get values from the supposed matrix in constant time.
7. Before the encryption and decryption we also take xor of original data with XOR value that we generated earlier from user key.
