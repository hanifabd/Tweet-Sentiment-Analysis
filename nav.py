from dsmodule import *

def menu():
    print('Apa yang ingin anda lakukan?')
    print('1. Update Data')
    print('2. Update Nilai Sentiment')
    print('3. Lihat Data')
    print('4. Visualisasi')
    print('5. Keluar')
    print('Input anda :')
    selection = input()

    if selection == '1': 
        updateData()
        print('\n')
        menu()
    elif selection == '2': 
        updateSentiment()
        print('\n')
        menu()
    elif selection == '3':
        print('tanggal awal (format: 2020-08-12) :')
        awal = input()
        print('tanggal akhir (format: 2020-08-12) :')
        akhir = input()
        df = lihatData(awal, akhir)
        print(df)
        print('\n')
        menu()
    elif selection == '4': 
        print('tanggal awal (format: 2020-08-12) :')
        awal = input()
        print('tanggal akhir (format: 2020-08-12) :')
        akhir = input()
        visualize(awal, akhir)
        print('\n')
        menu()
    elif selection == '5': 
        quit()
    else: 
        print("Unknown Option Selected!")
        print('\n')
        menu()