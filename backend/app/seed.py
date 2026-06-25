from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Organization, Shipment, User, Role

Base.metadata.create_all(bind=engine)

def run():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == 'admin').first():
            db.add(User(
                username='admin',
                full_name='Адміністратор системи',
                password_hash=hash_password('admin12345'),
                role=Role.SYSTEM_ADMIN.value,
                department='ГУ',
            ))
        if not db.query(Organization).first():
            org = Organization(name='Тестова організація', edrpou='00000000', address='м. Київ', responsible_person='Іваненко І.І.')
            db.add(org)
            db.flush()
            db.add(Shipment(
                barcode='PKSKDK-000001', sender_org_id=org.id, recipient_name='Отримувач 1',
                recipient_address='м. Київ, вул. Прикладна, 1', document_number='12/34',
                access_mark='НЕ СЕКРЕТНО', region='Київ', district='Печерський'
            ))
        db.commit()
        print('Seed completed: admin/admin12345')
    finally:
        db.close()

if __name__ == '__main__':
    run()
