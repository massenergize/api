from _main_ import settings


def run():
  if not settings.IS_PROD:
    return "Please set IS_PROD value to True"
  
  return "ALL GOOD - Ready for Launch"

if __name__ == "__main__":
  res = run()
  print(res)