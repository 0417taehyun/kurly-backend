carts = [{"id" : 1, "num" : ""}, {"id" : 2, "num" : "hi"}]
# for i in carts:
#     print(i['num'])

data = {
    'cart':[
        {
            'cart_id'             : cart['id'],
            'product_image'       : cart['num']
        } if cart['num'] else cart['num'] == "f" for cart in carts]
}
# tests = [20, 30]
# c = [ x if x == 20 else x * 3 for x in tests ]

print(data)