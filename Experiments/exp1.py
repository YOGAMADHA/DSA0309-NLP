
import re

text = "Python is easy. My number is 9876543210."

match_result = re.match(r"Python", text)
search_result = re.search(r"easy", text)
numbers = re.findall(r"\d+", text)

print("Match:", match_result.group() if match_result else "Not found")
print("Search:", search_result.group() if search_result else "Not found")
print("Numbers:", numbers)
