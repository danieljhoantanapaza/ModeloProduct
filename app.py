
from flask import Flask, request, redirect, url_for, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///productos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return (
            f"Product(id={self.id}, name='{self.name}', "
            f"price={self.price}, stock={self.stock})"
        )


@app.route("/")
def index():
    products = Product.query.order_by(Product.id).all()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>CRUD de Productos</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 10px; }
            th { background: #e8e8e8; }
            a, button { margin-right: 8px; }
            input { padding: 8px; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>Gestión de Productos</h1>

        <h2>Registrar producto</h2>
        <form action="/crear" method="post">
            <input name="name" placeholder="Nombre" required>
            <input name="price" type="number" step="any"
                   min="0" placeholder="Precio" required>
            <input name="stock" type="number" min="0"
                   placeholder="Stock (por defecto 0)">
            <button type="submit">Guardar</button>
        </form>

        <h2>Lista de productos</h2>
        <table>
            <tr>
                <th>ID</th><th>Nombre</th><th>Precio</th>
                <th>Stock</th><th>Acciones</th>
            </tr>
            {% for p in products %}
            <tr>
                <td>{{ p.id }}</td>
                <td>{{ p.name }}</td>
                <td>{{ "%.2f"|format(p.price) }}</td>
                <td>{{ p.stock }}</td>
                <td>
                    <a href="/editar/{{ p.id }}">Editar</a>
                    <form action="/eliminar/{{ p.id }}" method="post"
                          style="display:inline">
                        <button type="submit">Eliminar</button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="5">No hay productos registrados.</td></tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, products=products)

@app.route("/crear", methods=["POST"])
def crear():
    name = request.form["name"].strip()

    try:
        price = float(request.form["price"])
        stock = int(request.form.get("stock") or 0)

        if not name or price < 0 or stock < 0:
            raise ValueError("Datos no válidos")

        product = Product(name=name, price=price, stock=stock)
        db.session.add(product)
        db.session.commit()

    except (ValueError, TypeError):
        db.session.rollback()
        return "Datos incorrectos. Verifica nombre, precio y stock.", 400

    return redirect(url_for("index"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    product = db.session.get(Product, id)

    if product is None:
        return "Producto no encontrado", 404

    if request.method == "POST":
        name = request.form["name"].strip()

        try:
            price = float(request.form["price"])
            stock = int(request.form["stock"])

            if not name or price < 0 or stock < 0:
                raise ValueError("Datos no válidos")

            product.name = name
            product.price = price
            product.stock = stock
            db.session.commit()
            return redirect(url_for("index"))

        except (ValueError, TypeError):
            db.session.rollback()
            return "Datos incorrectos.", 400

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Editar producto</title></head>
    <body>
        <h1>Editar producto {{ product.id }}</h1>
        <form method="post">
            <label>Nombre:</label>
            <input name="name" value="{{ product.name }}" required><br>
            <label>Precio:</label>
            <input name="price" type="number" step="any" min="0"
                   value="{{ product.price }}" required><br>
            <label>Stock:</label>
            <input name="stock" type="number" min="0"
                   value="{{ product.stock }}" required><br>
            <button type="submit">Actualizar</button>
        </form>
        <a href="/">Volver</a>
    </body>
    </html>
    """, product=product)

@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    product = db.session.get(Product, id)

    if product is None:
        return "Producto no encontrado", 404

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    print("Base de datos creada satisfactoriamente")
    app.run(debug=True)
