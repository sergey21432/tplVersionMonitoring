#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def get_mattermost_channels(server_url, token):
    """
    Получает список каналов из Mattermost
    
    Args:
        server_url: URL сервера Mattermost (например: https://your-mattermost.com)
        token: Personal Access Token
    """
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Получаем список каналов
    response = requests.get(
        f'{server_url}/api/v4/channels',
        headers=headers
    )
    
    if response.status_code == 200:
        channels = response.json()
        print("Доступные каналы:")
        print("-" * 50)
        for channel in channels:
            print(f"Название: {channel['name']}")
            print(f"ID: {channel['id']}")
            print(f"Тип: {channel['type']}")
            print(f"Описание: {channel.get('header', 'Нет описания')}")
            print("-" * 50)
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

def get_mattermost_teams(server_url, token):
    """
    Получает список команд из Mattermost
    """
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        f'{server_url}/api/v4/teams',
        headers=headers
    )
    
    if response.status_code == 200:
        teams = response.json()
        print("Доступные команды:")
        print("-" * 50)
        for team in teams:
            print(f"Название: {team['name']}")
            print(f"ID: {team['id']}")
            print(f"Отображаемое название: {team['display_name']}")
            print("-" * 50)
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Замените на ваши данные
    SERVER_URL = "https://your-mattermost-server.com"
    TOKEN = "your-personal-access-token"
    
    print("=== Команды Mattermost ===")
    get_mattermost_teams(SERVER_URL, TOKEN)
    
    print("\n=== Каналы Mattermost ===")
    get_mattermost_channels(SERVER_URL, TOKEN)

