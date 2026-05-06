using Godot;
using Game.Godot.Adapters;
using Game.Godot.Scripts.Prototypes;

namespace Game.Godot.Scripts.UI;

public partial class MainMenu : Control
{
    private Button _btnPlay = default!;
    private Button _btnPrototype = default!;
    private Button _btnSettings = default!;
    private Button _btnQuit = default!;

    public override void _Ready()
    {
        _btnPlay = GetNode<Button>("VBox/BtnPlay");
        _btnPrototype = GetNode<Button>("VBox/BtnPrototype");
        _btnSettings = GetNode<Button>("VBox/BtnSettings");
        _btnQuit = GetNode<Button>("VBox/BtnQuit");

        _btnPlay.Pressed += OnPlayPressed;
        _btnPrototype.Pressed += OnPrototypePressed;
        _btnSettings.Pressed += OnSettingsPressed;
        _btnQuit.Pressed += OnQuitPressed;
    }

    public void ShowMenu() => Visible = true;
    public void HideMenu() => Visible = false;

    private void Publish(string type, string source, string dataJson = "{}")
    {
        var bus = GetNodeOrNull<EventBusAdapter>("/root/EventBus");
        bus?.PublishSimple(type, source, dataJson);
    }

    private void OnPlayPressed()
    {
        Publish("ui.menu.start", "ui");
        HideMenu();
    }

    private void OnSettingsPressed()
    {
        Publish("ui.menu.settings", "ui");
    }

    private void OnPrototypePressed()
    {
        var slug = PrototypeCatalog.DefaultMenuPrototypeSlug;
        var scenePath = PrototypeCatalog.DefaultMenuPrototypeScenePath;
        Publish(
            "ui.menu.prototype",
            "ui",
            $"{{\"slug\":\"{slug}\",\"scene_path\":\"{scenePath}\"}}"
        );
        HideMenu();
    }

    private void OnQuitPressed()
    {
        Publish("ui.menu.quit", "ui");
        GetTree().Quit();
    }
}
