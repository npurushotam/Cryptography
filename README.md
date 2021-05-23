# Cryptography
A cascaded cryptography system based on an idea of using armstrong numbers and matrices for encryption/decryption which was published in a research paper. 

In this program the basic idea is that user will provide a key based on that key file will get encrypted and same key must be used to decrypt the file. During encryption and decryption original file is divided into many chunks and process of encryption/decryption is done simultaneously which is achived by use of multithreading.

### How file is process during encryption/decryption
1. To process file there are two classes in the program named FileProcessor and ChunkProcessor. 
2. FileProcessor class takes in the file and divided it into N (8 in our case) chunks.
3. Each of these chunks are given to ChunkProcessor class along with key and command for encryption/decryption.
4. Then in the constructor of this class for the process of encryption/decryption new thread gets created and activated.
5. Each chunk gets processed byte by byte and gets stored in a target file, which in the end gets merged in the FileProcessor class.
6. After merging and getting final encrypted/decrypted file, target files for each chunk created earlier gets deleted using ```os.remove()```.
