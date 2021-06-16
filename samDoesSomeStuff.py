list1 = []

x = 0

list1.append([])

list1[x].append("hiya")
list1[x].append("235")

print(list1)

list1.append([])

x += 1

list1[x].append("hiya")
list1[x].append("235")

print(list1)

print(list1[0][1])