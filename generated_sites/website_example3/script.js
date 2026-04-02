const CONFIG = {
    website: 'website_example3',
    apiUrl: '/api/website_example3'
};

const state = {
    currentPage: 'home',
    products: [],
    cart: [],
    wishlist: [],
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false
};

// --- API Methods ---
const api = {
    async fetchProducts() {
        const res = await fetch(`${CONFIG.apiUrl}/products`);
        const data = await res.json();
        return data.products || [];
    },
    async fetchProductById(id) {
        const res = await fetch(`${CONFIG.apiUrl}/product/${id}`);
        const data = await res.json();
        return data.product;
    },
    async getCart() {
        const res = await fetch(`${CONFIG.apiUrl}/cart`);
        return await res.json();
    },
    async addToCart(productId) {
        const res = await fetch(`${CONFIG.apiUrl}/cart/${productId}`, { method: 'POST' });
        return await res.json();
    },
    async removeFromCart(productId) {
        const res = await fetch(`${CONFIG.apiUrl}/cart/${productId}`, { method: 'DELETE' });
        return await res.json();
    },
    async getWishlist() {
        const res = await fetch(`${CONFIG.apiUrl}/wishlist`);
        return await res.json();
    },
    async toggleWishlist(productId, inWishlist) {
        const method = inWishlist ? 'DELETE' : 'POST';
        const res = await fetch(`${CONFIG.apiUrl}/wishlist/${productId}`, { method });
        return await res.json();
    },
    async checkout() {
        const res = await fetch(`${CONFIG.apiUrl}/checkout`, { method: 'POST' });
        return await res.json();
    },
    async login(credentials) {
        const res = await fetch(`${CONFIG.apiUrl}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });
        return await res.json();
    },
    async register(details) {
        const res = await fetch(`${CONFIG.apiUrl}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(details)
        });
        return await res.json();
    }
};

// --- Router & UI Controller ---
const router = {
    async navigate(page, params = null) {
        state.currentPage = page;
        window.scrollTo(0, 0);
        this.render();
        
        if (page === 'home') this.renderHome();
        if (page === 'plp') this.renderPLP();
        if (page === 'pdp') this.renderPDP(params);
        if (page === 'cart') this.renderCart();
        if (page === 'wishlist') this.renderWishlist();
        if (page === 'checkout') this.renderCheckout();
    },

    render() {
        const app = document.getElementById('app-root');
        app.innerHTML = `<div class="flex justify-center py-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div></div>`;
        this.updateHeader();
    },

    updateHeader() {
        const authBtn = document.getElementById('auth-buttons');
        if (state.user) {
            authBtn.innerHTML = `
                <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Hi, ${state.user.name || 'User'}</span>
                <button onclick="auth.logout()" class="text-xs text-rose-500 font-bold">LOGOUT</button>
            `;
        } else {
            authBtn.innerHTML = `
                <button onclick="auth.showModal('login')" class="text-sm font-semibold hover:text-indigo-600">Login</button>
                <button onclick="auth.showModal('register')" class="bg-slate-900 text-white px-4 py-2 rounded-full text-sm">Sign Up</button>
            `;
        }
        
        const cartCount = document.getElementById('cart-count');
        if (state.cart.length > 0) {
            cartCount.innerText = state.cart.length;
            cartCount.classList.remove('hidden');
        } else {
            cartCount.classList.add('hidden');
        }
    },

    async renderHome() {
        const products = await api.fetchProducts();
        state.products = products;
        const featured = products.slice(0, 4);
        
        document.getElementById('app-root').innerHTML = `
            <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="relative bg-slate-900 rounded-3xl overflow-hidden mb-16">
                    <div class="absolute inset-0 bg-gradient-to-r from-black/70 to-transparent z-10"></div>
                    <img src="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&q=80&w=2000" class="w-full h-[500px] object-cover" />
                    <div class="absolute inset-0 z-20 flex flex-col justify-center px-12 text-white">
                        <span class="uppercase tracking-widest text-indigo-400 font-semibold mb-4">New Collection 2024</span>
                        <h1 class="text-5xl md:text-7xl font-bold mb-6">Define Your <br/>Style Signature.</h1>
                        <button onclick="router.navigate('plp')" class="bg-white text-slate-900 px-8 py-4 rounded-full font-bold w-max hover:bg-indigo-600 hover:text-white transition-all transform hover:scale-105">Shop Collection</button>
                    </div>
                </div>

                <div class="mb-20">
                    <div class="flex justify-between items-end mb-10">
                        <div>
                            <h2 class="text-3xl font-bold">Featured Styles</h2>
                            <p class="text-slate-500">Handpicked essentials for your wardrobe.</p>
                        </div>
                        <button onclick="router.navigate('plp')" class="text-indigo-600 font-bold border-b-2 border-indigo-600 pb-1">View All</button>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                        ${featured.map(p => this.productCard(p)).join('')}
                    </div>
                </div>
            </section>
        `;
    },

    async renderPLP() {
        const products = await api.fetchProducts();
        document.getElementById('app-root').innerHTML = `
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex flex-col md:flex-row justify-between items-center mb-12 gap-4">
                    <h1 class="text-4xl font-bold">Explore All Products</h1>
                    <div class="flex gap-4">
                        <select class="bg-white border border-slate-200 rounded-lg px-4 py-2 outline-none">
                            <option>Sort by: Newest</option>
                            <option>Price: Low to High</option>
                            <option>Price: High to Low</option>
                        </select>
                    </div>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                    ${products.map(p => this.productCard(p)).join('')}
                </div>
            </div>
        `;
    },

    async renderPDP(id) {
        const product = await api.fetchProductById(id);
        document.getElementById('app-root').innerHTML = `
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-16">
                    <div class="space-y-4">
                        <img src="${product.image_url}" class="w-full aspect-[4/5] object-cover rounded-3xl shadow-xl" />
                        <div class="grid grid-cols-4 gap-4">
                            <div class="bg-slate-200 aspect-square rounded-xl overflow-hidden">
                                <img src="${product.image_url}" class="w-full h-full object-cover opacity-50" />
                            </div>
                        </div>
                    </div>
                    <div class="flex flex-col justify-center">
                        <nav class="flex mb-6 text-sm text-slate-400 gap-2">
                            <span class="cursor-pointer hover:text-indigo-600" onclick="router.navigate('home')">Home</span>
                            <span>/</span>
                            <span class="cursor-pointer hover:text-indigo-600" onclick="router.navigate('plp')">Products</span>
                        </nav>
                        <h1 class="text-4xl font-bold mb-4">${product.title}</h1>
                        <div class="flex items-center gap-4 mb-6">
                            <span class="text-3xl font-bold text-indigo-600">$${product.special_price}</span>
                            <span class="text-xl text-slate-400 line-through">$${product.mrp}</span>
                            <span class="bg-rose-100 text-rose-600 px-2 py-1 rounded text-xs font-bold">-${Math.round((product.mrp - product.special_price) / product.mrp * 100)}%</span>
                        </div>
                        <p class="text-slate-600 mb-8 leading-relaxed">
                            Elevate your daily rotation with this premium ${product.name}. Crafted from sustainable materials and designed for both comfort and aesthetic appeal. 
                            A versatile addition to any modern wardrobe.
                        </p>
                        <div class="space-y-4 mb-10">
                            <div class="flex items-center gap-4">
                                <span class="font-bold w-20">Status:</span>
                                <span class="${product.stock_count > 0 ? 'text-green-600' : 'text-rose-600'} font-medium">
                                    ${product.stock_status} (${product.stock_count} units left)
                                </span>
                            </div>
                        </div>
                        <div class="flex gap-4">
                            <button onclick="actions.addToCart(${product.id})" class="flex-1 bg-indigo-600 text-white py-4 rounded-full font-bold hover:bg-indigo-700 transition transform active:scale-95">Add to Bag</button>
                            <button onclick="actions.toggleWishlist(${product.id})" class="p-4 border border-slate-200 rounded-full hover:bg-slate-50">
                                <i class="far fa-heart text-xl"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    async renderCart() {
        const data = await api.getCart();
        state.cart = data.cart || [];
        const app = document.getElementById('app-root');

        if (state.cart.length === 0) {
            app.innerHTML = `
                <div class="flex flex-col items-center justify-center py-20 text-center">
                    <div class="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6 text-slate-300">
                        <i class="fas fa-shopping-bag text-4xl"></i>
                    </div>
                    <h2 class="text-2xl font-bold mb-2">Your bag is empty</h2>
                    <p class="text-slate-500 mb-8">Looks like you haven't added anything yet.</p>
                    <button onclick="router.navigate('plp')" class="bg-indigo-600 text-white px-8 py-3 rounded-full font-bold">Start Shopping</button>
                </div>
            `;
            return;
        }

        app.innerHTML = `
            <div class="max-w-4xl mx-auto px-4">
                <h1 class="text-3xl font-bold mb-10">Shopping Bag (${data.total_items})</h1>
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-12">
                    <div class="lg:col-span-2 space-y-6">
                        ${state.cart.map(item => `
                            <div class="flex gap-6 pb-6 border-b border-slate-100">
                                <img src="${item.product.image}" class="w-24 h-32 object-cover rounded-xl" />
                                <div class="flex-1">
                                    <div class="flex justify-between mb-1">
                                        <h3 class="font-bold">${item.product.title}</h3>
                                        <span class="font-bold">$${item.product.price}</span>
                                    </div>
                                    <p class="text-xs text-slate-400 mb-4">Added on ${new Date(item.added_date).toLocaleDateString()}</p>
                                    <div class="flex justify-between items-center">
                                        <div class="flex items-center border rounded-lg">
                                            <button class="px-3 py-1">-</button>
                                            <span class="px-3 py-1 font-medium">${item.quantity}</span>
                                            <button class="px-3 py-1">+</button>
                                        </div>
                                        <button onclick="actions.removeFromCart(${item.product_id})" class="text-rose-500 text-sm font-medium">Remove</button>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 h-max">
                        <h3 class="font-bold text-lg mb-6">Order Summary</h3>
                        <div class="space-y-4 mb-6">
                            <div class="flex justify-between text-slate-500"><span>Subtotal</span><span>$${data.total_price}</span></div>
                            <div class="flex justify-between text-slate-500"><span>Shipping</span><span class="text-green-600">FREE</span></div>
                            <div class="border-t pt-4 flex justify-between font-bold text-xl"><span>Total</span><span>$${data.total_price}</span></div>
                        </div>
                        <button onclick="router.navigate('checkout')" class="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold hover:bg-indigo-700 transition">Proceed to Checkout</button>
                    </div>
                </div>
            </div>
        `;
    },

    async renderWishlist() {
        const data = await api.getWishlist();
        state.wishlist = data.wishlist || [];
        const app = document.getElementById('app-root');

        app.innerHTML = `
            <div class="max-w-7xl mx-auto px-4">
                <h1 class="text-3xl font-bold mb-10">My Wishlist</h1>
                ${state.wishlist.length === 0 ? 
                    `<p class="text-slate-500">Your wishlist is empty.</p>` : 
                    `<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                        ${state.wishlist.map(item => this.productCard({
                            id: item.product_id, 
                            title: item.product.title, 
                            special_price: item.product.price, 
                            mrp: item.product.price * 1.2,
                            image_url: item.product.image
                        })).join('')}
                    </div>`}
            </div>
        `;
    },

    async renderCheckout() {
        if (!state.user) {
            auth.showModal('login');
            return;
        }
        const data = await api.getCart();
        document.getElementById('app-root').innerHTML = `
            <div class="max-w-xl mx-auto px-4">
                <div class="bg-white rounded-3xl p-10 shadow-sm border border-slate-100">
                    <h1 class="text-3xl font-bold mb-8">Checkout</h1>
                    <form onsubmit="actions.processCheckout(event)" class="space-y-6">
                        <div class="grid grid-cols-2 gap-4">
                            <div class="col-span-2">
                                <label class="block text-sm font-bold mb-2">Shipping Address</label>
                                <input required type="text" placeholder="Street Address" class="w-full bg-slate-50 border-none rounded-xl px-4 py-3">
                            </div>
                            <input required type="text" placeholder="City" class="bg-slate-50 border-none rounded-xl px-4 py-3">
                            <input required type="text" placeholder="Postal Code" class="bg-slate-50 border-none rounded-xl px-4 py-3">
                        </div>
                        <div>
                            <label class="block text-sm font-bold mb-2">Payment Details</label>
                            <div class="bg-slate-900 text-white p-6 rounded-2xl relative overflow-hidden">
                                <div class="flex justify-between items-start mb-10 relative z-10">
                                    <i class="fas fa-microchip text-3xl text-yellow-400"></i>
                                    <i class="fab fa-visa text-4xl"></i>
                                </div>
                                <p class="text-lg tracking-[0.2em] mb-4 relative z-10">**** **** **** 4242</p>
                                <div class="flex justify-between text-xs opacity-60 relative z-10">
                                    <span>CARD HOLDER: ${state.user.name}</span>
                                    <span>EXPIRES: 12/26</span>
                                </div>
                                <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-white/5 rounded-full"></div>
                            </div>
                        </div>
                        <div class="bg-indigo-50 p-6 rounded-2xl space-y-2">
                           <div class="flex justify-between text-sm"><span>Order Subtotal</span><span class="font-bold">$${data.total_price}</span></div>
                           <div class="flex justify-between text-sm"><span>Tax (GST)</span><span class="font-bold">$${(data.total_price * 0.1).toFixed(2)}</span></div>
                           <div class="flex justify-between text-lg pt-2 border-t border-indigo-100"><span>Total Amount</span><span class="font-bold text-indigo-600">$${(data.total_price * 1.1).toFixed(2)}</span></div>
                        </div>
                        <button type="submit" class="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold shadow-lg shadow-indigo-200">Place Order & Pay</button>
                    </form>
                </div>
            </div>
        `;
    },

    productCard(p) {
        return `
            <div class="group relative">
                <div class="aspect-[3/4] w-full overflow-hidden rounded-2xl bg-slate-200 relative">
                    <img src="${p.image_url}" class="h-full w-full object-cover transition duration-500 group-hover:scale-110">
                    <button onclick="event.stopPropagation(); actions.toggleWishlist(${p.id})" class="absolute top-4 right-4 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md opacity-0 group-hover:opacity-100 transition">
                        <i class="far fa-heart"></i>
                    </button>
                    <div class="absolute bottom-0 left-0 w-full p-4 translate-y-full group-hover:translate-y-0 transition duration-300">
                        <button onclick="event.stopPropagation(); actions.addToCart(${p.id})" class="w-full bg-slate-900 text-white py-3 rounded-xl font-bold text-sm shadow-xl">
                            Add to Bag
                        </button>
                    </div>
                </div>
                <div class="mt-4 flex justify-between items-start" onclick="router.navigate('pdp', ${p.id})">
                    <div class="cursor-pointer">
                        <h3 class="text-sm font-bold text-slate-700">${p.title}</h3>
                        <p class="mt-1 text-sm text-slate-500">Modern Essential</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm font-bold text-indigo-600">$${p.special_price}</p>
                        <p class="text-xs text-slate-400 line-through">$${p.mrp}</p>
                    </div>
                </div>
            </div>
        `;
    }
};

// --- App Actions ---
const actions = {
    async addToCart(id) {
        try {
            const res = await api.addToCart(id);
            if (res.success) {
                utils.toast("Added to bag!", "success");
                // Sync global cart count
                const cartData = await api.getCart();
                state.cart = cartData.cart || [];
                router.updateHeader();
            }
        } catch (e) { console.error(e); }
    },
    async removeFromCart(id) {
        await api.removeFromCart(id);
        router.renderCart();
        router.updateHeader();
    },
    async toggleWishlist(id) {
        const inWishlist = state.wishlist.some(w => w.product_id === id);
        const res = await api.toggleWishlist(id, inWishlist);
        if (res.success) {
            utils.toast(inWishlist ? "Removed from wishlist" : "Saved to wishlist");
            const wlData = await api.getWishlist();
            state.wishlist = wlData.wishlist || [];
            router.updateHeader();
            if(state.currentPage === 'wishlist') router.renderWishlist();
        }
    },
    async processCheckout(e) {
        e.preventDefault();
        const res = await api.checkout();
        if (res.success) {
            document.getElementById('app-root').innerHTML = `
                <div class="max-w-md mx-auto text-center py-20 px-4">
                    <div class="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-8">
                        <i class="fas fa-check text-4xl"></i>
                    </div>
                    <h1 class="text-3xl font-bold mb-4">Order Confirmed!</h1>
                    <p class="text-slate-500 mb-8">Your order #${res.order.order_id} has been placed successfully. Check your email for details.</p>
                    <button onclick="router.navigate('home')" class="bg-slate-900 text-white px-8 py-3 rounded-full font-bold">Back to Home</button>
                </div>
            `;
            state.cart = [];
            router.updateHeader();
        }
    }
};

// --- Auth Controller ---
const auth = {
    showModal(type) {
        const modal = document.getElementById('modal-overlay');
        const content = document.getElementById('modal-content');
        modal.classList.remove('hidden');
        modal.classList.add('flex');

        if (type === 'login') {
            content.innerHTML = `
                <button onclick="auth.closeModal()" class="absolute top-4 right-4 text-slate-400 hover:text-slate-900"><i class="fas fa-times"></i></button>
                <h2 class="text-2xl font-bold mb-2">Welcome Back</h2>
                <p class="text-slate-500 mb-8">Please enter your details to sign in.</p>
                <form onsubmit="auth.handleLogin(event)" class="space-y-4">
                    <input required id="l-email" type="email" placeholder="Email Address" class="w-full bg-slate-50 border-none rounded-xl px-4 py-4">
                    <input required id="l-pass" type="password" placeholder="Password" class="w-full bg-slate-50 border-none rounded-xl px-4 py-4">
                    <button class="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold shadow-lg shadow-indigo-100">Sign In</button>
                </form>
                <p class="mt-6 text-center text-sm text-slate-500">Don't have an account? <a href="#" onclick="auth.showModal('register')" class="text-indigo-600 font-bold">Sign Up</a></p>
            `;
        } else {
            content.innerHTML = `
                <button onclick="auth.closeModal()" class="absolute top-4 right-4 text-slate-400 hover:text-slate-900"><i class="fas fa-times"></i></button>
                <h2 class="text-2xl font-bold mb-2">Create Account</h2>
                <p class="text-slate-500 mb-8">Join our community today.</p>
                <form onsubmit="auth.handleRegister(event)" class="space-y-4">
                    <input required id="r-name" type="text" placeholder="Full Name" class="w-full bg-slate-50 border-none rounded-xl px-4 py-4">
                    <input required id="r-email" type="email" placeholder="Email Address" class="w-full bg-slate-50 border-none rounded-xl px-4 py-4">
                    <input required id="r-pass" type="password" placeholder="Password" class="w-full bg-slate-50 border-none rounded-xl px-4 py-4">
                    <button class="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold shadow-lg shadow-indigo-100">Register Now</button>
                </form>
                <p class="mt-6 text-center text-sm text-slate-500">Already a member? <a href="#" onclick="auth.showModal('login')" class="text-indigo-600 font-bold">Log In</a></p>
            `;
        }
    },
    closeModal() {
        const modal = document.getElementById('modal-overlay');
        modal.classList.add('hidden');
    },
    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('l-email').value;
        const password = document.getElementById('l-pass').value;
        const res = await api.login({ email, password });
        if (res.success) {
            state.user = { email, user_id: res.user_id, name: email.split('@')[0] };
            localStorage.setItem('user', JSON.stringify(state.user));
            this.closeModal();
            router.updateHeader();
            utils.toast("Login successful!");
        }
    },
    async handleRegister(e) {
        e.preventDefault();
        const name = document.getElementById('r-name').value;
        const email = document.getElementById('r-email').value;
        const password = document.getElementById('r-pass').value;
        const res = await api.register({ name, email, password });
        if (res.success) {
            utils.toast("Registration successful! Please login.");
            this.showModal('login');
        }
    },
    logout() {
        state.user = null;
        localStorage.removeItem('user');
        router.updateHeader();
        router.navigate('home');
        utils.toast("Logged out");
    }
};

// --- Helpers ---
const utils = {
    toast(msg, type = "info") {
        const toast = document.getElementById('toast');
        document.getElementById('toast-message').innerText = msg;
        toast.classList.remove('translate-y-20', 'opacity-0');
        setTimeout(() => {
            toast.classList.add('translate-y-20', 'opacity-0');
        }, 3000);
    }
};

// Initial Boot
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize data from API
    try {
        const cartData = await api.getCart();
        state.cart = cartData.cart || [];
        const wlData = await api.getWishlist();
        state.wishlist = wlData.wishlist || [];
    } catch(e) { }
    
    router.navigate('home');
});