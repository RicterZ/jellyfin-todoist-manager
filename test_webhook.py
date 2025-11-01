import requests
import json
import time
from typing import Dict, Any

# API endpoint
BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/webhook"


def test_item_added_event():
    """Test Item Added event - creates Todoist section if needed, then creates task"""
    print("\n" + "="*60)
    print("Testing Item Added Event")
    print("Note: This will create a Todoist section 'Test Series' in the configured project if it doesn't exist")
    print("="*60)
    
    # Mock data for Item Added event
    mock_data = {
        "NotificationType": "ItemAdded",
        "Name": "Item Added",
        "ServerId": "test-server-123",
        "ServerName": "Test Jellyfin Server",
        "ServerVersion": "10.8.0",
        "ServerUrl": "http://localhost:8096",
        "Timestamp": "2024-01-15T10:30:00Z",
        "UtcTimestamp": "2024-01-15T10:30:00Z",
        "Id": "test-jellyfin-item-123",
        "ItemId": "test-jellyfin-item-123",
        "ItemName": "Test Episode Name",
        "ItemType": "Episode",
        "ItemPath": "/media/test/episode.mkv",
        "SeriesName": "Test Series",
        "SeasonNumber": "1",
        "EpisodeNumber": "1"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=mock_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Item Added event test PASSED")
            print("   → Should create/find section 'Test Series' in the configured project")
            print("   → Should create task in the section")
            return True
        else:
            print(f"❌ Item Added event test FAILED: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return False


def test_item_added_different_series():
    """Test Item Added event with different series name"""
    print("\n" + "="*60)
    print("Testing Item Added Event (Different Series)")
    print("Note: This will create a Todoist section 'Another Test Series' in the configured project if it doesn't exist")
    print("="*60)
    
    # Mock data for Item Added event with different series
    mock_data = {
        "NotificationType": "ItemAdded",
        "Name": "Item Added",
        "ServerId": "test-server-123",
        "ServerName": "Test Jellyfin Server",
        "ServerVersion": "10.8.0",
        "ServerUrl": "http://localhost:8096",
        "Timestamp": "2024-01-15T10:31:00Z",
        "UtcTimestamp": "2024-01-15T10:31:00Z",
        "Id": "test-jellyfin-item-456",
        "ItemId": "test-jellyfin-item-456",
        "ItemName": "Another Episode",
        "ItemType": "Episode",
        "ItemPath": "/media/test/episode2.mkv",
        "SeriesName": "Another Test Series",
        "SeasonNumber": "2",
        "EpisodeNumber": "5"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=mock_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Item Added (Different Series) event test PASSED")
            print("   → Should create/find section 'Another Test Series' in the configured project")
            print("   → Should create task in the new section")
            return True
        else:
            print(f"❌ Item Added (Different Series) event test FAILED: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return False


def test_playback_stop_event_completed():
    """Test Playback Stop event with completed status"""
    print("\n" + "="*60)
    print("Testing Playback Stop Event (Completed)")
    print("="*60)
    
    # Mock data for Playback Stop event - completed (within 1 minute)
    mock_data = {
        "NotificationType": "PlaybackStop",
        "Name": "Playback Stop",
        "ServerId": "test-server-123",
        "ServerName": "Test Jellyfin Server",
        "ServerVersion": "10.8.0",
        "ServerUrl": "http://localhost:8096",
        "Timestamp": "2024-01-15T10:35:00Z",
        "UtcTimestamp": "2024-01-15T10:35:00Z",
        "Id": "test-jellyfin-item-123",
        "ItemId": "test-jellyfin-item-123",
        "ItemName": "Test Episode Name",
        "ItemType": "Episode",
        "ItemPath": "/media/test/episode.mkv",
        "SeriesName": "Test Series",
        "SeasonNumber": "1",
        "EpisodeNumber": "1",
        "RunTime": "00:23:35",
        "PlaybackPosition": "00:23:00"  # 35 seconds difference (< 1 minute)
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=mock_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Playback Stop (Completed) event test PASSED")
            return True
        else:
            print(f"❌ Playback Stop (Completed) event test FAILED: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return False


def test_playback_stop_event_incomplete():
    """Test Playback Stop event with incomplete status"""
    print("\n" + "="*60)
    print("Testing Playback Stop Event (Incomplete)")
    print("="*60)
    
    # Mock data for Playback Stop event - incomplete (> 1 minute difference)
    mock_data = {
        "NotificationType": "PlaybackStop",
        "Name": "Playback Stop",
        "ServerId": "test-server-123",
        "ServerName": "Test Jellyfin Server",
        "ServerVersion": "10.8.0",
        "ServerUrl": "http://localhost:8096",
        "Timestamp": "2024-01-15T10:35:00Z",
        "UtcTimestamp": "2024-01-15T10:35:00Z",
        "Id": "test-jellyfin-item-incomplete",
        "ItemId": "test-jellyfin-item-incomplete",
        "ItemName": "Incomplete Episode",
        "ItemType": "Episode",
        "ItemPath": "/media/test/episode.mkv",
        "SeriesName": "Test Series",
        "SeasonNumber": "1",
        "EpisodeNumber": "2",
        "RunTime": "00:23:35",
        "PlaybackPosition": "00:10:00"  # 13 minutes 35 seconds difference (> 1 minute)
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=mock_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Playback Stop (Incomplete) event test PASSED")
            return True
        else:
            print(f"❌ Playback Stop (Incomplete) event test FAILED: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return False


def test_unknown_event():
    """Test unknown event type"""
    print("\n" + "="*60)
    print("Testing Unknown Event")
    print("="*60)
    
    mock_data = {
        "NotificationType": "UnknownEvent",
        "Name": "Unknown Event",
        "ServerId": "test-server-123",
        "ServerName": "Test Jellyfin Server"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=mock_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Unknown event test PASSED (should be ignored)")
            return True
        else:
            print(f"❌ Unknown event test FAILED: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending request: {e}")
        return False


def check_server_running():
    """Check if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Jellyfin Todoist Manager - Webhook Test Suite")
    print("="*60)
    
    # Check if server is running
    print("\nChecking if server is running...")
    if not check_server_running():
        print("❌ Server is not running!")
        print("Please start the server first:")
        print("  python main.py")
        return
    
    print("✅ Server is running")
    
    # Run tests
    results = []
    
    # Test 1: Item Added event (creates section if needed)
    results.append(("Item Added", test_item_added_event()))
    
    # Wait a bit for database and Todoist operation
    time.sleep(2)
    
    # Test 2: Item Added with different series (tests section creation)
    results.append(("Item Added (Different Series)", test_item_added_different_series()))
    
    # Wait a bit for database operation
    time.sleep(2)
    
    # Test 3: Playback Stop (Completed)
    results.append(("Playback Stop (Completed)", test_playback_stop_event_completed()))
    
    # Test 4: Playback Stop (Incomplete)
    results.append(("Playback Stop (Incomplete)", test_playback_stop_event_incomplete()))
    
    # Test 5: Unknown event
    results.append(("Unknown Event", test_unknown_event()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed")


if __name__ == "__main__":
    main()

