# Новий блок додається так:
# 1) створити backend/app/modules/<module_name>/router.py
# 2) створити backend/app/modules/<module_name>/__init__.py з registry.register(...)
# 3) додати імпорт нижче.
import app.modules.organizations
import app.modules.registries
import app.modules.shipments
import app.modules.scanner
import app.modules.search
import app.modules.reports
import app.modules.analytics
import app.modules.admin
import app.modules.workflow
import app.modules.organization_structure
import app.modules.user_management
import app.modules.document_management
import app.modules.audit_log
import app.modules.file_storage
import app.modules.notifications
import app.modules.reporting_analytics
import app.modules.administration
