#ifndef WEBSOCKETCLIENT_H
#define WEBSOCKETCLIENT_H

#include <websocketpp/client.hpp>
#include <websocketpp/config/asio_no_tls_client.hpp>
#include <string>
#include <functional>
#include <map>
#include <iostream>
#include <thread>
#include <memory>

// 用于打包opus二进制数据的协议
struct BinProtocol {
    uint16_t version;
    uint16_t type;
    uint32_t payload_size;
    uint8_t payload[];
} __attribute__((packed));

struct BinProtocolInfo {
    uint16_t version;
    uint16_t type;
};

class WebSocketClient {
public:
    using message_callback_t = std::function<void(const std::string&, bool)>;
    using close_callback_t = std::function<void()>;

    WebSocketClient(const std::string& address, int port, const std::string& token, const std::string& deviceId, int protocolVersion);
    ~WebSocketClient();

    void Run();
    void Connect();
    void Close();
    void Terminate();
    void SendText(const std::string& message);
    void SendBinary(const uint8_t* data, size_t size);
    void SetMessageCallback(message_callback_t callback);
    void SetCloseCallback(close_callback_t callback);
    bool IsConnected() const { return is_connected_; }

private:
    using client_t = websocketpp::client<websocketpp::config::asio_client>;
    client_t ws_client_;
    websocketpp::lib::shared_ptr<websocketpp::lib::thread> thread_;
    websocketpp::connection_hdl connection_hdl_;
    std::map<std::string, std::string> headers_;
    message_callback_t on_message_;
    close_callback_t on_close_;
    std::string uri_;
    bool is_connected_ = false;

    void on_open(websocketpp::connection_hdl hdl);
    void on_message(websocketpp::connection_hdl hdl, client_t::message_ptr msg);
    void on_close(websocketpp::connection_hdl hdl);
};

#endif // WEBSOCKETCLIENT_H
