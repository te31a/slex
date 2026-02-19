import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404

from base_app.models import Filial, Contracts, Menu
from base_app.pg_utils import (
    get_good_by_marking_goods,
    get_goods_list_by_marking_goods,
    query_goods_stock_by_group_id_ok,
    query_goods_stock_by_group_id,
)
from base_app.contract_models import neo_stroy_krd
from base_app.contract_models.rnd import ok

logger = logging.getLogger(__name__)

# Реестр обработчиков контрактов.
# Для добавления нового сервиса — добавить запись: 'slug-контракта': модуль_обработчик
dict_module = {
    'neo-stroj-rostov': neo_stroy_krd,
    'ok': ok,
}


@login_required
def home(request):
    context = {
        'title': 'Главная',
        'filial': Filial.objects.filter(as_active=True),
    }
    return render(request, 'base_app/home.html', context=context)


@login_required
def home_filial(request, _filial_slug):
    context = {
        'menu': Menu.objects.filter(as_active=True, filial__slug=_filial_slug),
        'prefix': _filial_slug,
    }
    return render(request, 'base_app/home_filial.html', context=context)


@login_required
def list_view_contracts(request, _filial_slug):
    context = {
        'contracts': Contracts.objects.filter(as_active=True, filial__slug=_filial_slug),
        'prefix': _filial_slug,
    }
    return render(request, 'base_app/contracts.html', context=context)


@login_required
def detail_view_contracts(request, _contract_slug, _filial_slug):
    _contract = get_object_or_404(
        Contracts, as_active=True, filial__slug=_filial_slug, slug=_contract_slug
    )
    context = {
        'result': False,
        'contract': _contract,
        'contracts': Contracts.objects.filter(as_active=True, filial__slug=_filial_slug),
        'prefix': _filial_slug,
    }
    return render(request, 'base_app/contract_menu.html', context=context)


@login_required
def handler_data_form(request, _contract_slug, _filial_slug):
    """Единая точка входа для всех операций на странице контракта."""
    _contract = get_object_or_404(
        Contracts, filial__slug=_filial_slug, slug=_contract_slug
    )
    context = {
        'result': False,
        'msg': False,
        'error_msg': False,
        'df_res': None,
        'contract': _contract,
        'contracts': Contracts.objects.filter(as_active=True, filial__slug=_filial_slug),
        'prefix': _filial_slug,
    }

    if request.method != 'POST':
        return render(request, 'base_app/contract_menu.html', context=context)

    if 'orders' in request.POST:
        # ---------- Импорт файла заявки ----------
        file = request.FILES.get('file', False)
        if not file:
            context['error_msg'] = True
            context['msg'] = 'Файл не выбран.'
        elif _contract_slug not in dict_module:
            context['error_msg'] = True
            context['msg'] = f'Обработчик для контракта «{_contract_slug}» не настроен.'
        else:
            try:
                res, error_valid = dict_module[_contract_slug].start(file, _contract)
                if error_valid:
                    context['error_msg'] = True
                    context['msg'] = f'Ошибка обработки: {res}'
                    logger.error('Ошибка обработки заявки контракт=%s: %s', _contract_slug, res)
                else:
                    context['result'] = res
                    context['msg'] = 'Успешно!'
            except Exception as exc:
                logger.exception('Неожиданная ошибка при обработке заявки контракт=%s', _contract_slug)
                context['error_msg'] = True
                context['msg'] = f'Неожиданная ошибка: {exc}'

    elif 'stocks' in request.POST:
        # ---------- Получить остатки по группе товаров ----------
        group_id = _contract.id_groups_goods
        try:
            if _contract_slug == 'ok':
                df_res = query_goods_stock_by_group_id_ok(id_group_goods=group_id, _contract=_contract)
            else:
                df_res = query_goods_stock_by_group_id(id_group_goods=group_id, _contract=_contract)
            context['df_res'] = df_res.to_html(classes='content-table', index=False, border=0)
        except Exception as exc:
            logger.exception('Ошибка получения остатков контракт=%s', _contract_slug)
            context['error_msg'] = True
            context['msg'] = f'Ошибка получения остатков: {exc}'

    elif 'product_one' in request.POST:
        # ---------- Проверить один товар по артикулу ----------
        marking = request.POST.get('art', '').strip()
        if not marking:
            context['error_msg'] = True
            context['msg'] = 'Введите артикул.'
        else:
            try:
                df_res = get_good_by_marking_goods(_marking_goods=int(marking), _contract=_contract)
                context['df_res'] = df_res.to_html(classes='content-table', index=False, border=0)
            except ValueError:
                context['error_msg'] = True
                context['msg'] = 'Артикул должен быть числом.'
            except Exception as exc:
                logger.exception('Ошибка поиска товара контракт=%s арт=%s', _contract_slug, marking)
                context['error_msg'] = True
                context['msg'] = f'Ошибка поиска товара: {exc}'

    elif 'product_all' in request.POST:
        # ---------- Проверить список товаров по Excel ----------
        file = request.FILES.get('file', False)
        if not file:
            context['error_msg'] = True
            context['msg'] = 'Файл не выбран.'
        else:
            try:
                df_res = get_goods_list_by_marking_goods(_file_marking_goods=file, _contract=_contract)
                context['df_res'] = df_res.to_html(classes='content-table', index=False, border=0)
            except Exception as exc:
                logger.exception('Ошибка проверки списка товаров контракт=%s', _contract_slug)
                context['error_msg'] = True
                context['msg'] = f'Ошибка проверки товаров: {exc}'

    return render(request, 'base_app/contract_menu.html', context=context)


class Login(LoginView):
    template_name = 'base_app/login.html'

    def get_success_url(self):
        return super().get_success_url()


class NotFound(LoginView):
    template_name = 'base_app/not_groups.html'

    def get_success_url(self):
        return super().get_success_url()


def logout_view(request):
    logout(request)
    return redirect('home')
