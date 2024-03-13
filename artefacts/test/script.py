if __name__ == '__main__':

    to_generate = 'plume.txt'

    with open(to_generate, 'w') as file:
        # crits total = 22 (score = 207.4)
        for i in range(6, 17):
            file.write('any\n')
            file.write('a = 311\n')
            file.write('cr = {:.1f}'.format(i*3.3)+'\n')
            file.write('cd = {:.1f}'.format((22-i)*6.6)+'\n\n')


