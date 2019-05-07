import click

from storage.services import StorageService
from storage.model import Container
from tabulate import tabulate
from datetime import datetime

@click.group()
def storage():
    """Manages access credentials containers"""
    pass

@storage.command()
@click.option('-n', '--name_page', 
    type = str,
    prompt = True,
    help = 'The page name')
@click.option('-a', '--address',
    type = str,
    prompt = True,
    help = 'The page address')
@click.option('-u', '--user',
    type = str,
    prompt = True,
    help = 'User account')
@click.password_option()
@click.pass_context
def create(ctx, name_page, address, user, password):
    """Create a new container of credentials."""
    container = Container(name_page, address, user,password)
    storage_service = StorageService(ctx.obj['pages_table'])
    storage_service.create_container(container)
    click.echo('Container created...')


@storage.command()
@click.argument('option', type = str, default = '-s')
@click.argument('container_uid', type = str)
def delete(ctx, option, container_uid):
    """Delete a container"""
    storage_service = StorageService(ctx.obj['pages_table'])
    container_list = storage_service.list_clients('-n')
    container = [container for container in container_list if container['uid'] == container_uid]
    if click.confirm(f'Are you sure you want to delete the container with uid: {container_uid}') and container:
        if option == '-s':
            container = _soft_delete_credentials_flow(Container(**container[0]))
            storage_service.update_container(container)
            click.echo('Container deleted...')
        elif option == '-f':
            storage_service.delete_container(container_uid)
            click.echo('Container deleted...')
    else:
        click.echo('Container not found...')


def _soft_delete_credentials_flow(container):
    container.deleted_at = datetime.now()
    return container


@clients.command()
@click.argument('container_uid', type = str)
@click.pass_context
def update(ctx, container_uid):
    """Update a container"""
    storage_service = StorageService(ctx.obj['clients_table'])
    container_list = storage_service.list_clients('-n')
    container = [container for container in container_list if container['uid'] == container_uid]
    if container:
        container = _update_credentials_flow(Container(**container[0]))
        storage_service.update_container(container)
        click.echo('Container updated...')
    else:
        click.echo('Container not found...')


def _update_credentials_flow(container):
    click.echo('Leave empty if you don\'t want to modify the value?')
    container.name_page = click.prompt('New name', type = str, default = container.name_page)
    container.address = click.prompt('New lastname', type = str, default = container.address)
    container.user = click.prompt('New company', type = str, default = container.user)
    container.password = click.prompt('New email', type = str, default = container.password)
    container.updated_at = datetime.now()
    return container


@storage.command()
@click.argument('option', type = str, default = '-n')
@click.pass_context
def list(ctx, option):
    """List the stored data"""
    storage_service = StorageService(ctx.obj['pages_table'])
    container_list = storage_service.list_containers(option)
    click.echo(tabulate(container_list, headers = 'keys', tablefmt='fancy_grid'))


@storage.command()
@click.argument('name_page', type = str)
@click.pass_context
def search(ctx, name_page):
    """Search container for name page"""
    storage_service = StorageService(ctx.obj['pages_table'])
    containers = storage_service.search(name_page)
    if containers:
        click.echo(tabulate(containers, headers = 'keys', tablefmt='fancy_grid'))
    else:
        click.echo('Container not found...')


all = storage