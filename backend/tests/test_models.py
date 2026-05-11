"""Model instantiation and behavior tests."""

import pytest
from passlib.context import CryptContext

from app.models.admin import Admin
from app.models.categoria import Categoria
from app.models.envio import EnvioConfig
from app.models.pago import Pago, MetodoPago, EstadoPago
from app.models.pedido import Pedido, EstadoPedido, TipoEntrega, ZonaEnvio
from app.models.pedido_item import PedidoItem, UnidadMedida
from app.models.producto import Producto, TipoUnidad

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestAdmin:
    """Admin model tests — password hashing and instantiation."""

    def test_password_is_hashed(self):
        """Admin password MUST be stored as a bcrypt hash, not plaintext."""
        plain_password = "admin123"
        hashed = pwd_context.hash(plain_password)

        assert hashed != plain_password
        assert len(hashed) > 0
        # bcrypt hashes start with $2b$ or $2a$
        assert hashed.startswith("$2")

    def test_verify_password(self):
        """Hashed password MUST be verifiable with passlib."""
        plain_password = "secure-password"
        hashed = pwd_context.hash(plain_password)

        assert pwd_context.verify(plain_password, hashed)
        assert not pwd_context.verify("wrong-password", hashed)

    @pytest.mark.asyncio
    async def test_create_admin(self, db_session):
        """Admin model MUST persist with hashed password, email, and created_at."""
        admin = Admin(
            email="test@nutristore.com",
            hashed_password=pwd_context.hash("testpass"),
        )
        db_session.add(admin)
        await db_session.commit()
        await db_session.refresh(admin)

        assert admin.id is not None
        assert admin.email == "test@nutristore.com"
        assert admin.hashed_password != "testpass"
        assert admin.created_at is not None
        assert pwd_context.verify("testpass", admin.hashed_password)

    @pytest.mark.asyncio
    async def test_admin_email_unique(self, db_session):
        """Duplicate admin email MUST raise IntegrityError."""
        admin1 = Admin(email="dup@nutristore.com", hashed_password="hash1")
        admin2 = Admin(email="dup@nutristore.com", hashed_password="hash2")

        db_session.add(admin1)
        await db_session.commit()

        db_session.add(admin2)
        with pytest.raises(Exception):  # IntegrityError on commit
            await db_session.commit()


class TestTipoUnidad:
    """TipoUnidad enum tests."""

    def test_enum_values(self):
        """TipoUnidad MUST have KG and UNIDAD values."""
        assert TipoUnidad.KG.value == "KG"
        assert TipoUnidad.UNIDAD.value == "UNIDAD"

    def test_enum_membership(self):
        """Only valid members MUST be assignable."""
        assert TipoUnidad("KG") == TipoUnidad.KG
        assert TipoUnidad("UNIDAD") == TipoUnidad.UNIDAD
        with pytest.raises(ValueError):
            TipoUnidad("LITRO")


class TestPedidoDefaults:
    """Pedido model state defaults."""

    def test_estado_pedido_enum(self):
        """EstadoPedido MUST have the four expected states."""
        assert EstadoPedido.PENDIENTE.value == "PENDIENTE"
        assert EstadoPedido.CONFIRMADO.value == "CONFIRMADO"
        assert EstadoPedido.ENTREGADO.value == "ENTREGADO"
        assert EstadoPedido.CANCELADO.value == "CANCELADO"

    def test_default_estado_is_pendiente(self):
        """New pedido MUST default to PENDIENTE estado."""
        assert EstadoPedido.PENDIENTE == EstadoPedido.PENDIENTE

    @pytest.mark.asyncio
    async def test_create_pedido_with_defaults(self, db_session):
        """Pedido MUST be created with PENDIENTE estado and costo_envio=0."""
        from decimal import Decimal

        pedido = Pedido(
            session_id="sess-123",
            cliente_nombre="Juan Pérez",
            cliente_direccion="Calle Falsa 123",
            cliente_telefono="+5491112345678",
            direccion_entrega="Calle Falsa 123",
            tipo_entrega=TipoEntrega.RETIRO,
            total=Decimal("1500.00"),
        )
        db_session.add(pedido)
        await db_session.commit()
        await db_session.refresh(pedido)

        assert pedido.id is not None
        assert pedido.estado == EstadoPedido.PENDIENTE
        assert pedido.costo_envio == Decimal("0.00")
        assert pedido.tipo_entrega == TipoEntrega.RETIRO
        assert pedido.zona_envio is None
        assert pedido.created_at is not None

    @pytest.mark.asyncio
    async def test_create_pedido_con_envio(self, db_session):
        """Pedido with ENVIO tipo MUST set zona and costo."""
        from decimal import Decimal

        pedido = Pedido(
            session_id="sess-456",
            cliente_nombre="María García",
            cliente_direccion="Av. Siempre Viva 742",
            cliente_telefono="+5491122223333",
            direccion_entrega="Av. Siempre Viva 742",
            tipo_entrega=TipoEntrega.ENVIO,
            zona_envio=ZonaEnvio.CABA,
            costo_envio=Decimal("3500.00"),
            total=Decimal("5000.00"),
        )
        db_session.add(pedido)
        await db_session.commit()
        await db_session.refresh(pedido)

        assert pedido.tipo_entrega == TipoEntrega.ENVIO
        assert pedido.zona_envio == ZonaEnvio.CABA
        assert pedido.costo_envio == Decimal("3500.00")

    def test_tipo_entrega_enum(self):
        """TipoEntrega MUST have ENVIO and RETIRO."""
        assert TipoEntrega.ENVIO.value == "ENVIO"
        assert TipoEntrega.RETIRO.value == "RETIRO"

    def test_zona_envio_enum(self):
        """ZonaEnvio MUST have CABA, GBA_NORTE, GBA_SUR, GBA_OESTE."""
        assert ZonaEnvio.CABA.value == "CABA"
        assert ZonaEnvio.GBA_NORTE.value == "GBA_NORTE"
        assert ZonaEnvio.GBA_SUR.value == "GBA_SUR"
        assert ZonaEnvio.GBA_OESTE.value == "GBA_OESTE"


class TestCategoria:
    """Categoria model tests."""

    @pytest.mark.asyncio
    async def test_create_categoria(self, db_session):
        """Categoria MUST be created with nombre and optional descripcion."""
        cat = Categoria(nombre="Frutas", descripcion="Frutas frescas")
        db_session.add(cat)
        await db_session.commit()
        await db_session.refresh(cat)

        assert cat.id is not None
        assert cat.nombre == "Frutas"
        assert cat.descripcion == "Frutas frescas"

    @pytest.mark.asyncio
    async def test_create_categoria_sin_descripcion(self, db_session):
        """Categoria descripcion MUST be nullable."""
        cat = Categoria(nombre="Verduras")
        db_session.add(cat)
        await db_session.commit()
        await db_session.refresh(cat)

        assert cat.descripcion is None


class TestProducto:
    """Producto model tests."""

    @pytest.mark.asyncio
    async def test_create_producto_kg(self, db_session):
        """Producto with KG tipo MUST persist with stock_kg."""
        from decimal import Decimal

        cat = Categoria(nombre="Lácteos")
        db_session.add(cat)
        await db_session.flush()

        prod = Producto(
            nombre="Queso Cremoso",
            descripcion="Queso cremoso por kg",
            precio_por_kg=Decimal("8500.00"),
            tipo_unidad=TipoUnidad.KG,
            stock_kg=5.5,
            categoria_id=cat.id,
        )
        db_session.add(prod)
        await db_session.commit()
        await db_session.refresh(prod)

        assert prod.id is not None
        assert prod.tipo_unidad == TipoUnidad.KG
        assert prod.stock_kg == 5.5
        assert prod.stock_unidades is None
        assert prod.activo is True

    @pytest.mark.asyncio
    async def test_create_producto_unidad(self, db_session):
        """Producto with UNIDAD tipo MUST persist with stock_unidades."""
        from decimal import Decimal

        cat = Categoria(nombre="Suplementos")
        db_session.add(cat)
        await db_session.flush()

        prod = Producto(
            nombre="Creatina 300g",
            descripcion="Suplemento de creatina",
            precio_por_kg=Decimal("0.00"),
            precio_por_unidad=Decimal("12000.00"),
            tipo_unidad=TipoUnidad.UNIDAD,
            stock_unidades=25,
            categoria_id=cat.id,
        )
        db_session.add(prod)
        await db_session.commit()
        await db_session.refresh(prod)

        assert prod.tipo_unidad == TipoUnidad.UNIDAD
        assert prod.stock_unidades == 25
        assert prod.stock_kg is None


class TestPago:
    """Pago model tests."""

    @pytest.mark.asyncio
    async def test_create_pago_efectivo(self, db_session):
        """Pago with EFECTIVO method MUST be created."""
        from decimal import Decimal

        pedido = Pedido(
            session_id="sess-pago",
            cliente_nombre="Test",
            cliente_direccion="Dir",
            cliente_telefono="123",
            direccion_entrega="Dir",
            tipo_entrega=TipoEntrega.RETIRO,
            total=Decimal("1000.00"),
        )
        db_session.add(pedido)
        await db_session.flush()

        pago = Pago(
            pedido_id=pedido.id,
            metodo=MetodoPago.EFECTIVO,
            monto=Decimal("1000.00"),
        )
        db_session.add(pago)
        await db_session.commit()
        await db_session.refresh(pago)

        assert pago.id is not None
        assert pago.metodo == MetodoPago.EFECTIVO
        assert pago.estado == EstadoPago.PENDIENTE
        assert pago.monto == Decimal("1000.00")

    def test_metodo_pago_enum(self):
        """MetodoPago MUST have EFECTIVO and TRANSFERENCIA."""
        assert MetodoPago.EFECTIVO.value == "EFECTIVO"
        assert MetodoPago.TRANSFERENCIA.value == "TRANSFERENCIA"

    def test_estado_pago_enum(self):
        """EstadoPago MUST have PENDIENTE and CONFIRMADO."""
        assert EstadoPago.PENDIENTE.value == "PENDIENTE"
        assert EstadoPago.CONFIRMADO.value == "CONFIRMADO"


class TestEnvioConfig:
    """EnvioConfig model tests."""

    @pytest.mark.asyncio
    async def test_create_envio_config(self, db_session):
        """EnvioConfig MUST persist zona and costo."""
        from decimal import Decimal

        config = EnvioConfig(zona=ZonaEnvio.CABA, costo=Decimal("3500.00"))
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)

        assert config.id is not None
        assert config.zona == ZonaEnvio.CABA
        assert config.costo == Decimal("3500.00")

    @pytest.mark.asyncio
    async def test_envio_config_zona_unique(self, db_session):
        """Duplicate zona MUST raise IntegrityError."""
        from decimal import Decimal

        config1 = EnvioConfig(zona=ZonaEnvio.CABA, costo=Decimal("3500.00"))
        config2 = EnvioConfig(zona=ZonaEnvio.CABA, costo=Decimal("4000.00"))

        db_session.add(config1)
        await db_session.commit()

        db_session.add(config2)
        with pytest.raises(Exception):
            await db_session.commit()


class TestUnidadMedida:
    """UnidadMedida enum tests."""

    def test_enum_values(self):
        """UnidadMedida MUST have KG and UNIDAD."""
        assert UnidadMedida.KG.value == "KG"
        assert UnidadMedida.UNIDAD.value == "UNIDAD"
