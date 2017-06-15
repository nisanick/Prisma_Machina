from datetime import datetime as date

year = date.now().timetuple().tm_year
print(year)
now = date.utcnow().replace(year=(year+1286)).strftime("%H:%m %d %b %Y")
print(now)