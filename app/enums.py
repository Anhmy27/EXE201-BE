from app.settings import DevConfig

ADMIN_EMAIL = DevConfig.ADMIN_EMAIL

ALLOWED_EXTENSIONS_IMG = ['.jpeg', '.jpg', '.png']

ADMIN_KEY_GROUP = 'admin'
USER_KEY_GROUP = "user"

TYPE_PAYMENT_ONLINE = {
    'MOMO': 'momo',
    'ZALO': 'zalo',
}

TYPE_PAYMENT = {
    'MOMO': 'momo',
    'ZALO': 'zalo',
}

TYPE_ACTION_SEND_MAIL = {
    'REGISTER': 'register',
    'OPEN_ACCOUNT': 'open_account',
    'UPDATE_ACCOUNT': 'update_account',
    'CHANGE_PASS': 'change_pass',
    'FORGET_PASS': 'forget_pass',
    'NEW_PASSWORD': 'new_password',
    'NEW_STAFF': 'new_staff',
}

TYPE_FILE_LINK = {
    'USER': 'user',
    'PRODUCT': 'product',
    'SESSION_COURSE': 'session_course'
}


MAIL_VERITY_CODE = 'verity_register'
GROUP_ADMIN_KEY = 'admin'
GROUP_USER_KEY = 'user'
GROUP_KEY_PARAM = {
    "is_admin": "/admin/product",
    "user": "/",
}

MOMO_CONFIG = {
    "momo_api_create_payment": "https://test-payment.momo.vn/v2/gateway/api/create",
    "momo_api_check_payment": "https://test-payment.momo.vn/v2/gateway/api/query",
    "redirectUrl": "about:blank",
    "accessKey": "F8BBA842ECF85",
    "secretKey": "K951B6PE1waDMi640xX08PD3vg6EkVlz",
    "partnerCode": "MOMO",
    "partnerName" : "MoMo Payment",
    "requestType": "payWithMethod",
    "extraData": "",
    "autoCapture": True,
    "lang": "vi",
    "storeId": "Test Store",
    "orderGroupId": "",
    "status_success": 0
}

ZALO_CONFIG = {
    "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
    "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
    "app_id":2553,
    "app_user": "user123",
    "bank_code": "zalopayapp",
    "zalo_api_create_payment": "https://sb-openapi.zalopay.vn/v2/create",
    "zalo_api_check_payment": "https://sb-openapi.zalopay.vn/v2/query",
    "status_success": 1
}

DURATION_SESSION_MINUTES = 100
