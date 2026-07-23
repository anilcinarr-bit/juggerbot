from app.models.coupon_result import classify_trendyol_result

# Test cases
test_cases = [
    'Geçersiz indirim kodu İndirim kodu sadece A-Z, 0-9 karakterlerini içermelidir.',
    'İndirim kodu geçersiz',
    'geçersiz indirim kodu',
    'daha önce kullanıldı',
    'minimum sepet tutarı sağlanmadı',
    'süresi dolmuş',
    'başarıyla uygulandı',
    'some random text'
]

print("Testing Trendyol classification:")
for test in test_cases:
    result = classify_trendyol_result(test)
    print(f'Input: "{test}" -> Output: {result.value}')