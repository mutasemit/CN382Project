import os
import secrets

class Config:
    # إنشاء مفتاح سري عشوائي للجلسات
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # إعدادات قاعدة البيانات SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mystudytasks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات الجلسات
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # مدة الجلسة بالثواني (ساعة واحدة)