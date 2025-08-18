from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Table
from datetime import date, time
import re
from decimal import Decimal

class BookingForm(forms.ModelForm):
    """Форма бронирования столика"""
    
    # Добавляем поле для выбора блюд
    selected_items = forms.MultipleChoiceField(
        choices=[],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Выберите блюда для предзаказа (необязательно)'
    )
    
    # Поле для предоплаты (только при предзаказе)
    deposit_amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=Decimal('0'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Сумма предоплаты (₽)',
        help_text='Требуется только при предзаказе блюд'
    )
    
    class Meta:
        model = Booking
        fields = ['name', 'phone', 'date', 'time', 'guests_count', 'comments']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'guests_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Ваше имя',
            'phone': 'Телефон',
            'date': 'Дата',
            'time': 'Время',
            'guests_count': 'Количество гостей',
            'comments': 'Комментарий',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Устанавливаем минимальную дату на сегодня
        self.fields['date'].widget.attrs['min'] = date.today().isoformat()
        
        # Создаем выбор времени с интервалом в 10 минут
        time_choices = []
        for hour in range(10, 22):  # с 10:00 до 21:00
            for minute in [0, 10, 20, 30, 40, 50]:
                time_str = f"{hour:02d}:{minute:02d}"
                time_choices.append((time_str, time_str))
        
        # Добавляем 22:00
        time_choices.append(('22:00', '22:00'))
        
        self.fields['time'] = forms.ChoiceField(
            choices=time_choices,
            label='Время',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        
        # Обновляем выбор столиков с описаниями
        table_choices = []
        tables = Table.objects.filter(is_available=True).order_by('number')
        for table in tables:
            description = f" - {table.description}" if table.description else ""
            table_choices.append((
                table.id, 
                f"Столик №{table.number} ({table.seats} мест){description}"
            ))
        
        self.fields['table'] = forms.ChoiceField(
            choices=table_choices,
            label='Столик',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        
        # Загружаем доступные блюда из меню
        try:
            from menu.models import MenuItem
            menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
            item_choices = []
            for item in menu_items:
                item_choices.append((
                    str(item.id), 
                    f"{item.name} - {item.price} ₽ ({item.category.name})"
                ))
            self.fields['selected_items'].choices = item_choices
        except ImportError:
            self.fields['selected_items'].choices = []
        
        # Если пользователь авторизован, предлагаем его имя как начальное значение
        if user and user.is_authenticated:
            full_name = f"{user.first_name} {user.last_name}".strip()
            if full_name:
                self.fields['name'].initial = full_name
    
    def clean_phone(self):
        """Проверка корректности телефона"""
        phone = self.cleaned_data['phone']
        
        # Удаляем все пробелы, дефисы, скобки и другие символы
        phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Проверяем, что остались только цифры
        if not phone_clean.isdigit():
            raise forms.ValidationError('Номер телефона должен содержать только цифры.')
        
        # Проверяем длину (должно быть 10-11 цифр для российских номеров)
        if len(phone_clean) < 10 or len(phone_clean) > 11:
            raise forms.ValidationError('Номер телефона должен содержать 10-11 цифр.')
        
        # Если 11 цифр, первая должна быть 7 или 8
        if len(phone_clean) == 11:
            if phone_clean[0] not in ['7', '8']:
                raise forms.ValidationError('Номер телефона должен начинаться с 7 или 8.')
        
        # Форматируем номер для сохранения
        if len(phone_clean) == 11:
            return f"+7{phone_clean[1:]}"
        else:
            return f"+7{phone_clean}"
    
    def clean_date(self):
        """Проверка даты"""
        booking_date = self.cleaned_data['date']
        if booking_date < date.today():
            raise forms.ValidationError('Нельзя бронировать на прошедшую дату.')
        return booking_date
    
    def clean_time(self):
        """Проверка времени"""
        time_str = self.cleaned_data['time']
        try:
            # Преобразуем строку времени в объект time для валидации
            hour, minute = map(int, time_str.split(':'))
            booking_time = time(hour, minute)
            
            if booking_time < time(10, 0) or booking_time > time(22, 0):
                raise forms.ValidationError('Ресторан работает с 10:00 до 22:00.')
            
            return time_str  # Возвращаем строку для сохранения в базе
        except ValueError:
            raise forms.ValidationError('Неверный формат времени.')
    
    def clean_deposit_amount(self):
        """Проверка суммы предоплаты"""
        deposit = self.cleaned_data.get('deposit_amount', 0)
        selected_items = self.data.getlist('selected_items', [])
        
        # Предоплата требуется только при предзаказе
        if selected_items and deposit < 500:
            raise forms.ValidationError('При предзаказе минимальная сумма предоплаты составляет 500 ₽.')
        
        return deposit or 0
    
    def clean(self):
        """Проверка всей формы"""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_str = cleaned_data.get('time')
        table = cleaned_data.get('table')
        guests_count = cleaned_data.get('guests_count')
        selected_items = cleaned_data.get('selected_items', [])
        deposit_amount = cleaned_data.get('deposit_amount', 0)
        
        # Проверяем, что количество гостей не превышает вместимость столика
        if table and guests_count:
            try:
                table_obj = Table.objects.get(id=int(table))
                if guests_count > table_obj.seats:
                    raise forms.ValidationError(f'Столик №{table_obj.number} вмещает максимум {table_obj.seats} человек.')
            except (Table.DoesNotExist, ValueError):
                pass
        
        if date and time_str and table:
            try:
                # Преобразуем строку времени в объект time для сравнения
                hour, minute = map(int, time_str.split(':'))
                booking_time = time(hour, minute)
                
                # Проверяем, не занят ли столик
                existing_booking = Booking.objects.filter(
                    table_id=int(table),
                    date=date,
                    time=time_str,
                    status__in=['pending', 'paid', 'confirmed']
                ).exists()
                
                if existing_booking:
                    raise forms.ValidationError('Этот столик уже забронирован на указанное время.')
            except ValueError:
                pass  # Ошибка времени уже обработана в clean_time
        
        # Рассчитываем сумму предзаказа
        preorder_total = Decimal('0')
        preorder_items = []
        
        if selected_items:
            try:
                from menu.models import MenuItem
                for item_id in selected_items:
                    try:
                        item = MenuItem.objects.get(id=item_id, is_available=True)
                        preorder_total += item.price
                        preorder_items.append({
                            'id': item.id,
                            'name': item.name,
                            'price': float(item.price),
                            'category': item.category.name
                        })
                    except MenuItem.DoesNotExist:
                        pass
            except ImportError:
                pass
        
        # Проверяем предоплату только при предзаказе
        if preorder_total > 0:
            min_deposit = max(Decimal('500'), preorder_total * Decimal('0.3'))  # 30% от суммы предзаказа
            if deposit_amount < min_deposit:
                raise forms.ValidationError(f'При предзаказе на сумму {preorder_total} ₽ минимальная предоплата составляет {min_deposit} ₽.')
        
        # Сохраняем рассчитанные данные
        cleaned_data['preorder_total'] = preorder_total
        cleaned_data['preorder_items'] = preorder_items
        cleaned_data['has_preorder'] = len(preorder_items) > 0
        
        return cleaned_data

class ContactForm(forms.Form):
    """Форма обратной связи"""
    name = forms.CharField(
        max_length=100,
        label='Ваше имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=200,
        label='Тема',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )

 