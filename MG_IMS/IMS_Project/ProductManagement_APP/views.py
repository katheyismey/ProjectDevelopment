from django.shortcuts import render

# Create your views here.
# inventory/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, ProductVersion, Supplier, StockLog
from .forms import ProductForm, CategoryForm, ProductVersionForm, SupplierForm
from django.urls import reverse
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils.timezone import now
from ExpensesTracker_APP.models import ExpenseLog

# Inventory list
def inventory_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('selected_category') # Get the selected category ID from the request
    search_query = request.GET.get('search', '').strip()  # Get search query from the request

    if selected_category:
        selected_category = int(selected_category) # Convert to integer
        products = Product.objects.filter(category__id=selected_category) # Filter products by selected category ID
    else:
        products = Product.objects.all() # Show all products if no category is selected

    # Apply search filter if a search query is provided
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(product_id__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
        
    # Annotate total_quantity to each product
    products = products.annotate(annotated_total_quantity=Sum('versions__product_quantity'))

    return render(request, 'inventory/inventory_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category, # Pass the selected category ID to the template
        'search_query': search_query, # Pass search query to template
    })
    
#Product Versions list
def product_versions(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    return render(request, 'inventory/product_versions.html', {'product': product})

# Add product
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)

        if product_form.is_valid():
            product_form.save()  # Save the product
            return redirect('ProductManagement_APP:inventory_list')  # Redirect to the inventory list page
    else:
        product_form = ProductForm()

    return render(request, 'inventory/add_product.html', {
        'product_form': product_form,
    })

# Edit product
def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        if product_form.is_valid():
            product_form.save()
            return redirect('ProductManagement_APP:inventory_list')
    else:
        product_form = ProductForm(instance=product)
    return render(request, 'inventory/edit_product.html', {'product_form': product_form})

# Delete product
def delete_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == "POST":
        product.delete()
        return redirect(reverse("ProductManagement_APP:inventory_list"))  # Redirect to inventory list after deletion
    
    # Render confirmation page on GET request
    return render(request, "inventory/confirm_delete_product.html", {"product": product})


# Add Product Version
def add_product_version(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        form = ProductVersionForm(request.POST)
        if form.is_valid():
            supplier = form.cleaned_data['supplier']
            product_quantity = form.cleaned_data['product_quantity']
            buying_price = form.cleaned_data['buying_price']
            
            # Create the new product version
            product_version = ProductVersion.objects.create(
                product=product,
                supplier=supplier,
                buying_price=buying_price,
                selling_price=form.cleaned_data['selling_price'],
                product_quantity=product_quantity,
                batch_id=form.cleaned_data['batch_id']
            )
            
            # Log the expense
            ExpenseLog.objects.create(
                product_version=product_version,
                quantity=product_quantity,
                buying_price=buying_price,
                total_cost=product_quantity * buying_price
            )
            return redirect('ProductManagement_APP:product_versions', product_id=product_id)
        else:
            messages.error(request, "There was an error with your form submission.")
    else:
        form = ProductVersionForm(initial={'product': product})
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/add_product_version.html', {'product': product, 'form': form, 'suppliers': suppliers})

#Edit product Version
def edit_product_version(request, version_id):
    version = get_object_or_404(ProductVersion, id=version_id)
    product_id = version.product.product_id  # Retrieve the product ID from the version object
    if request.method == 'POST':
        form = ProductVersionForm(request.POST, instance=version)
        if form.is_valid():
            form.save()
            return redirect('ProductManagement_APP:product_versions', product_id=product_id)  # Use the retrieved product_id
    else:
        form = ProductVersionForm(instance=version)
    return render(request, 'inventory/edit_product_version.html', {'form': form, 'version': version})

# Delete Product Version
def delete_product_version(request, version_id):
    
    version = get_object_or_404(ProductVersion, id=version_id)
    product_id = version.product.product_id 
    
    if request.method == 'POST':
        print(f"Deleting version ID: {version_id}")
        version.delete()
        return redirect('ProductManagement_APP:product_versions', product_id=product_id)
    
    return render(request, 'inventory/confirm_delete_product_version.html', {'version': version})

# Add category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ProductManagement_APP:inventory_list')  # Redirect to the inventory list page or any other relevant page
    else:
        form = CategoryForm()
    
    return render(request, 'inventory/add_category.html', {'form': form})

# Edit category
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('ProductManagement_APP:inventory_list')  # Adjust as needed
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/edit_category.html', {'form': form})

# Delete category
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == "POST":
        category.delete()
        return redirect(reverse("ProductManagement_APP:inventory_list"))  # Redirect to inventory list after deletion
    
    # Render confirmation page on GET request
    return render(request, "inventory/confirm_delete_category.html", {"category": category})

# Stock in
def stock_in(request, version_id):
    version = get_object_or_404(ProductVersion, id=version_id)
    product_id = version.product.product_id
    stock_in_logs = version.stock_logs.filter(action_type='IN').order_by('-timestamp')

    if request.method == 'POST':
        stock_in_amount = request.POST.get('stock_in_amount')
        if stock_in_amount:
            try:
                stock_in_amount = int(stock_in_amount)
                if stock_in_amount <= 0:
                    messages.error(request, "Amount must be greater than zero.")
                else:
                    version.product_quantity += stock_in_amount
                    version.save()
                    
                    # Create a new StockLog entry
                    StockLog.objects.create(
                        product_version=version,
                        action_type='IN',
                        quantity=stock_in_amount,
                        remarks=f"Added {stock_in_amount} units"
                    )
                    
                    # Log the expense
                    ExpenseLog.objects.create(
                        product_version=version,
                        quantity=stock_in_amount,
                        buying_price=version.buying_price,
                        total_cost=stock_in_amount * version.buying_price
                    )
                    
                    messages.success(request, f"{stock_in_amount} units added to stock.")
                    return redirect('ProductManagement_APP:product_versions', product_id=product_id)
            except ValueError:
                messages.error(request, "Invalid stock in amount. Please enter a valid number.")
        else:
            messages.error(request, "Stock in amount is required.")
    return render(request, 'inventory/stock_in.html', {
        'version': version,
        'stock_in_logs': stock_in_logs,
    })
    
# Stock out
def stock_out(request, version_id):
    version = get_object_or_404(ProductVersion, id=version_id)
    product_id = version.product.product_id 
    stock_out_logs = version.stock_logs.filter(action_type='OUT').order_by('-timestamp')  # Added this line to get stock-out logs

    if request.method == 'POST':
        stock_out_amount = request.POST.get('stock_out_amount')
        if stock_out_amount:
            try:
                stock_out_amount = int(stock_out_amount)
                # Ensure stock_out_amount is valid and doesn't exceed the available stock
                if version.product_quantity >= stock_out_amount:
                    version.product_quantity -= stock_out_amount
                    if version.product_quantity < 0:
                        messages.error(request, "Insufficient stock.")
                    else:
                        version.save()
                        
                        # Log the stock-out operation
                        stock_log_entry = StockLog.objects.create(
                            product_version=version,
                            quantity=stock_out_amount,  # Store as positive since it's stock-out
                            action_type='OUT',
                            remarks=f"Stock-out performed by user at {now()}"
                        )
                        
                        messages.success(request, f"{stock_out_amount} units removed from stock.")
                        return redirect('ProductManagement_APP:product_versions', product_id=product_id)
                else:
                    messages.error(request, "Insufficient stock.")
            except ValueError:
                messages.error(request, "Invalid stock out amount.")
        else:
            messages.error(request, "Stock out amount is required.")

    return render(request, 'inventory/stock_out.html', {'version': version, 'stock_out_logs': stock_out_logs})  # Added stock_out_logs to context


# Add supplier
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ProductManagement_APP:inventory_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/add_supplier.html', {'form': form})

