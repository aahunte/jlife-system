import pandas as pd

da = pd.read_excel("local.ods")
db = pd.read_excel("update.ods")
dc = pd.read_excel("swap.ods")
filec = dc.columns
db = db.rename(columns = {'中文姓名' : '姓名'})
db = db.rename(columns = {'居住類型' : '住屋類別'})
common_lines = da.columns.intersection(db.columns)
diff_lines = list(set(da.columns) - set(db.columns))
dc = da[diff_lines].head(517)
da = da[common_lines].head(517)
db = db[common_lines]
db['住屋類別'] = db['住屋類別'].str.rstrip(',')
temd = da.drop(columns = ['姓名', '家庭編號', '婚姻狀況', '年齡', '性別', '地址', '分流', '住屋類別'])
match_db = temd.merge(db, on="會員編號")
diff = da != match_db
db = db.sort_values(by = "會員編號")

wdata = db.reindex(columns = filec)
for col in wdata.columns:
    if col in dc.columns:
        wdata[col] = dc[col]
wdata.to_excel("swap.ods", index = False)
print(da)
print(match_db)
print(diff)
