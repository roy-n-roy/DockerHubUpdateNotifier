import schedule
import time

from manage import main


if __name__ == '__main__':

    schedule.every().hours.do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
