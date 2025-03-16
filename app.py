from Main import return_score

if __name__=='__main__':
    while(1):
        
        file,mes = return_score( input('title')+'\n\n'+input("essay :"),input('key :'))
        print(mes)