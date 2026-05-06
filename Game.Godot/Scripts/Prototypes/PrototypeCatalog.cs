using System.Collections.Generic;

namespace Game.Godot.Scripts.Prototypes;

public static class PrototypeCatalog
{
    public const string DefaultRpgPrototypeSlug = "default-rpg-template";
    public const string DefaultRpgPrototypeScenePath = "res://Game.Godot/Prototypes/DefaultRpgTemplate/DefaultRpgPrototype.tscn";

    public static readonly IReadOnlyDictionary<string, string> SceneBySlug = new Dictionary<string, string>
    {
        [DefaultRpgPrototypeSlug] = DefaultRpgPrototypeScenePath,
    };

    public static string DefaultMenuPrototypeSlug => DefaultRpgPrototypeSlug;

    public static string DefaultMenuPrototypeScenePath => ResolveScenePath(DefaultMenuPrototypeSlug);

    public static string ResolveScenePath(string slug)
    {
        return SceneBySlug.TryGetValue(slug, out var scenePath)
            ? scenePath
            : string.Empty;
    }
}
