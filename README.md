# price-steamlit-aomsin

# requirements.text

pip install streamlit

# update code
git status
>>>ต้องไม่เห็น >>>.streamlit/secrets.toml แล้วกด >>> ได้>>>
git add . ; git commit -m "update" ; git push origin main

----------------
ถ้าเผลอ add ไปแล้ว

ต้องลบออกจาก index ก่อน:

git rm --cached .streamlit/secrets.toml
git commit -m "remove secrets"
