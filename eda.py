import matplotlib.pyplot as plt

def plot_revenue_by_product(lines):
    product_revenue = {}

    for line in lines:
        product_name = line['product_id'][1]
        price_total = line['price_total']
        
        if product_name not in product_revenue:
            product_revenue[product_name] = 0.0
        product_revenue[product_name] += price_total

    products = list(product_revenue.keys())
    revenues = list(product_revenue.values())

    plt.figure(figsize=(10, 6))
    plt.bar(products, revenues, color='skyblue')
    plt.xlabel('Sản phẩm')
    plt.ylabel('Doanh thu (VND)')
    plt.title('Doanh thu theo sản phẩm')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return plt